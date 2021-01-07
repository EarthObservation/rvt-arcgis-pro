"""
Relief Visualization Toolbox – Visualization Functions

RVT multiple directions hillshade esri raster function
rvt_py, rvt.vis.multi_hillshade

Credits:
    Žiga Kokalj (ziga.kokalj@zrc-sazu.si)
    Krištof Oštir (kristof.ostir@fgg.uni-lj.si)
    Klemen Zakšek
    Klemen Čotar
    Maja Somrak
    Žiga Maroh

Copyright:
    2010-2020 Research Centre of the Slovenian Academy of Sciences and Arts
    2016-2020 University of Ljubljana, Faculty of Civil and Geodetic Engineering
"""

import numpy as np
import rvt.vis


class RVTMultiHillshade:
    def __init__(self):
        self.name = "RVT multi hillshade"
        self.description = "Calculates multiple directions hillshade."
        # default values
        self.nr_directions = 16.
        self.elevation = 35.
        self.calc_8_bit = False
        self.padding = 1
        self.fill_no_data = True
        self.keep_original_no_data = False

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
            },
            {
                'name': 'fill_no_data',
                'dataType': 'boolean',
                'value': self.fill_no_data,
                'required': True,
                'displayName': "Fill no-data (holes)",
                'description': "If True it fills no_data pixels with mean of neighbors (3x3)."
            },
            {
                'name': 'keep_original_no_data',
                'dataType': 'boolean',
                'value': self.keep_original_no_data,
                'required': True,
                'displayName': "Keep original no-data",
                'description': "If True (fill no-data has to be True) it keeps no-data from input raster. "
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(nr_directions=scalars.get('nr_directions'), elevation=scalars.get("sun_elevation"),
                     calc_8_bit=scalars.get("calc_8_bit"), fill_no_data=scalars.get("fill_no_data"),
                     keep_original_no_data=scalars.get("keep_original_no_data"))
        return {
            'compositeRasters': False,
            'inheritProperties': 2 | 4,
            'invalidateProperties': 2 | 4 | 8,
            'inputMask': False,
            'resampling': False,
            'padding': self.padding,
            'resamplingType': 4
        }

    def updateRasterInfo(self, **kwargs):
        kwargs['output_info']['noData'] = np.nan
        kwargs['output_info']['pixelType'] = 'f4'
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['statistics'] = int(self.nr_directions) * ({'minimum': -1, 'maximum': 1},)
        if self.calc_8_bit:
            kwargs['output_info']['bandCount'] = 3
        else:
            kwargs['output_info']['bandCount'] = int(self.nr_directions)
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        dem = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)[0]  # Input pixel array.
        pixel_size = props['cellSize']
        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]
        else:  # if no data is None we can't fill no data
            self.fill_no_data = False
            self.keep_original_no_data = False

        dict_slp_asp = rvt.vis.slope_aspect(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                            ve_factor=1, no_data=no_data, fill_no_data=self.fill_no_data,
                                            keep_original_no_data=self.keep_original_no_data)
        if self.calc_8_bit:  # calc 8 bit
            hillshade_r = rvt.vis.hillshade(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                            sun_azimuth=315, sun_elevation=self.elevation,
                                            slope=dict_slp_asp["slope"], aspect=dict_slp_asp["aspect"],
                                            no_data=no_data, fill_no_data=self.fill_no_data,
                                            keep_original_no_data=self.keep_original_no_data)
            hillshade_g = rvt.vis.hillshade(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                            sun_azimuth=22.5, sun_elevation=self.elevation,
                                            slope=dict_slp_asp["slope"], aspect=dict_slp_asp["aspect"],
                                            no_data=no_data, fill_no_data=self.fill_no_data,
                                            keep_original_no_data=self.keep_original_no_data)
            hillshade_b = rvt.vis.hillshade(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                            sun_azimuth=90, sun_elevation=self.elevation,
                                            slope=dict_slp_asp["slope"], aspect=dict_slp_asp["aspect"],
                                            no_data=no_data, fill_no_data=self.fill_no_data,
                                            keep_original_no_data=self.keep_original_no_data)
            hillshade_rgb = np.array([hillshade_r, hillshade_g, hillshade_b])
            hillshade_rgb = hillshade_rgb[:, self.padding:-self.padding, self.padding:-self.padding]  # remove padding
            pixelBlocks['output_pixels'] = hillshade_rgb.astype(props['pixelType'], copy=False)
        else:  # calc nr_directions
            multihillshade = rvt.vis.multi_hillshade(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                                     nr_directions=self.nr_directions, sun_elevation=self.elevation,
                                                     slope=dict_slp_asp["slope"], aspect=dict_slp_asp["aspect"],
                                                     no_data=no_data, fill_no_data=self.fill_no_data,
                                                     keep_original_no_data=self.keep_original_no_data)
            multihillshade = multihillshade[:, self.padding:-self.padding, self.padding:-self.padding]  # remove padding
            pixelBlocks['output_pixels'] = multihillshade.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def prepare(self, nr_directions=16, elevation=35, calc_8_bit=False, fill_no_data=True, keep_original_no_data=False):
        self.nr_directions = int(nr_directions)
        self.elevation = elevation
        self.calc_8_bit = calc_8_bit
        self.fill_no_data = fill_no_data
        self.keep_original_no_data = keep_original_no_data
