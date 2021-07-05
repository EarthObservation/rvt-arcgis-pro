"""
Relief Visualization Toolbox – Visualization Functions

RVT multiple directions hillshade esri raster function
rvt_py, rvt.vis.multi_hillshade

Credits:
    Žiga Kokalj (ziga.kokalj@zrc-sazu.si)
    Krištof Oštir (kristof.ostir@fgg.uni-lj.si)
    Klemen Zakšek
    Peter Pehani
    Klemen Čotar
    Maja Somrak
    Žiga Maroh

Copyright:
    2010-2020 Research Centre of the Slovenian Academy of Sciences and Arts
    2016-2020 University of Ljubljana, Faculty of Civil and Geodetic Engineering
"""

import numpy as np
import rvt.vis
import rvt.blend_func
import gc


class RVTMultiHillshade:
    def __init__(self):
        self.name = "RVT multi hillshade"
        self.description = "Calculates multiple directions hillshade."
        # default values
        self.nr_directions = 16.
        self.elevation = 35.
        self.calc_8_bit = False
        self.padding = 1
        # 8bit (bytscale) parameters
        self.mode_bytscl = "value"
        self.min_bytscl = 0
        self.max_bytscl = 1

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "Input raster for which to create the multiple directions hillshade map."
            },
            {
                'name': 'calc_8_bit',
                'dataType': 'boolean',
                'value': self.calc_8_bit,
                'required': False,
                'displayName': "Calculate 8-bit",
                'description': "If True it only calculates 8-bit (nr_directions doesn't matter),"
                               " in 3 directions (sun_azimuith = 315, 22.5, 90)"
            },
            {
                'name': 'nr_directions',
                'dataType': 'numeric',
                'value': self.nr_directions,
                'required': False,
                'displayName': "Number of directions",
                'description': "Number of directions for sun azimuth angle (clockwise from North)."
            },
            {
                'name': 'sun_elevation',
                'dataType': 'numeric',
                'value': self.elevation,
                'required': False,
                'displayName': "Sun elevation",
                'description': "Solar vertical angle (above the horizon) in degrees."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(nr_directions=scalars.get('nr_directions'), elevation=scalars.get("sun_elevation"),
                     calc_8_bit=scalars.get("calc_8_bit"))
        return {
            'compositeRasters': False,
            'inheritProperties': 2 | 4,
            'invalidateProperties': 2 | 4 | 8,
            'inputMask': False,
            'resampling': False,
            'padding': self.padding,
            'resamplingType': 1
        }

    def updateRasterInfo(self, **kwargs):
        kwargs['output_info']['noData'] = np.nan
        kwargs['output_info']['histogram'] = ()
        if self.calc_8_bit:
            kwargs['output_info']['pixelType'] = 'u1'
            kwargs['output_info']['bandCount'] = 3
            kwargs['output_info']['statistics'] = int(self.nr_directions) * ({'minimum': 0, 'maximum': 255},)
        else:
            kwargs['output_info']['pixelType'] = 'f4'
            kwargs['output_info']['bandCount'] = int(self.nr_directions)
            kwargs['output_info']['statistics'] = int(self.nr_directions) * ({'minimum': -1, 'maximum': 1},)
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        dem = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)[0]  # Input pixel array.
        pixel_size = props['cellSize']
        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]

        dict_slp_asp = rvt.vis.slope_aspect(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                            ve_factor=1, no_data=no_data, fill_no_data=False,
                                            keep_original_no_data=False)
        hillshade_r = None
        hillshade_g = None
        hillshade_b = None
        hillshade_rgb = None
        multihillshade = None

        if self.calc_8_bit:  # calc 8 bit
            hillshade_r = rvt.vis.hillshade(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                            sun_azimuth=315, sun_elevation=self.elevation,
                                            slope=dict_slp_asp["slope"], aspect=dict_slp_asp["aspect"],
                                            no_data=no_data, fill_no_data=False,
                                            keep_original_no_data=False)
            hillshade_g = rvt.vis.hillshade(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                            sun_azimuth=22.5, sun_elevation=self.elevation,
                                            slope=dict_slp_asp["slope"], aspect=dict_slp_asp["aspect"],
                                            no_data=no_data, fill_no_data=False,
                                            keep_original_no_data=False)
            hillshade_b = rvt.vis.hillshade(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                            sun_azimuth=90, sun_elevation=self.elevation,
                                            slope=dict_slp_asp["slope"], aspect=dict_slp_asp["aspect"],
                                            no_data=no_data, fill_no_data=False,
                                            keep_original_no_data=False)
            if self.mode_bytscl.lower() == "value":
                hillshade_r = rvt.blend_func.normalize_lin(image=hillshade_r, minimum=self.min_bytscl,
                                                           maximum=self.max_bytscl)
                hillshade_r = rvt.vis.byte_scale(data=hillshade_r, no_data=no_data)
                hillshade_g = rvt.blend_func.normalize_lin(image=hillshade_g, minimum=self.min_bytscl,
                                                           maximum=self.max_bytscl)
                hillshade_g = rvt.vis.byte_scale(data=hillshade_g, no_data=no_data)
                hillshade_b = rvt.blend_func.normalize_lin(image=hillshade_b, minimum=self.min_bytscl,
                                                           maximum=self.max_bytscl)
                hillshade_b = rvt.vis.byte_scale(data=hillshade_b, no_data=no_data)
            else:  # self.mode_bytscl == "perc" or "percent"
                hillshade_r = rvt.blend_func.normalize_perc(image=hillshade_r, minimum=self.min_bytscl,
                                                            maximum=self.max_bytscl)
                hillshade_r = rvt.vis.byte_scale(data=hillshade_r, no_data=no_data)
                hillshade_g = rvt.blend_func.normalize_perc(image=hillshade_g, minimum=self.min_bytscl,
                                                            maximum=self.max_bytscl)
                hillshade_g = rvt.vis.byte_scale(data=hillshade_g, no_data=no_data)
                hillshade_b = rvt.blend_func.normalize_perc(image=hillshade_b, minimum=self.min_bytscl,
                                                            maximum=self.max_bytscl)
                hillshade_b = rvt.vis.byte_scale(data=hillshade_b, no_data=no_data)

            hillshade_rgb = np.array([hillshade_r, hillshade_g, hillshade_b])
            hillshade_rgb = hillshade_rgb[:, self.padding:-self.padding, self.padding:-self.padding]  # remove padding

            pixelBlocks['output_pixels'] = hillshade_rgb.astype(props['pixelType'], copy=False)
        else:  # calc nr_directions
            multihillshade = rvt.vis.multi_hillshade(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                                     nr_directions=self.nr_directions, sun_elevation=self.elevation,
                                                     slope=dict_slp_asp["slope"], aspect=dict_slp_asp["aspect"],
                                                     no_data=no_data, fill_no_data=False,
                                                     keep_original_no_data=False)
            multihillshade = multihillshade[:, self.padding:-self.padding, self.padding:-self.padding]  # remove padding

            pixelBlocks['output_pixels'] = multihillshade.astype(props['pixelType'], copy=False)

        # release memory
        del dem
        del no_data
        del pixel_size
        del dict_slp_asp
        del hillshade_r
        del hillshade_g
        del hillshade_b
        del hillshade_rgb
        del multihillshade
        gc.collect()

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = 'MULTI-HS_D{}_H{}'.format(self.nr_directions, self.elevation)
            if self.calc_8_bit:
                keyMetadata['datatype'] = 'Processed'
                name += "_8bit"
            else:
                keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)

        if self.calc_8_bit:
            if bandIndex == 0:
                keyMetadata['bandname'] = 'HS_A{}_H{}_8bit'.format(315, self.elevation)
            elif bandIndex == 1:
                keyMetadata['bandname'] = 'HS_A{}_H{}_8bit'.format(22.5, self.elevation)
            elif bandIndex == 2:
                keyMetadata['bandname'] = 'HS_A{}_H{}_8bit'.format(90, self.elevation)
        else:
            for i_dir in range(self.nr_directions):
                if bandIndex == i_dir:
                    azimuth = (360 / self.nr_directions) * i_dir
                    keyMetadata['bandname'] = 'HS_A{}_H{}'.format(azimuth, self.elevation)
        return keyMetadata

    def prepare(self, nr_directions=16, elevation=35, calc_8_bit=False):
        self.nr_directions = int(nr_directions)
        self.elevation = float(elevation)
        self.calc_8_bit = calc_8_bit
