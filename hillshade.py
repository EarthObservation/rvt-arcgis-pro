"""
Relief Visualization Toolbox – Visualization Functions

RVT hillshade esri raster function
rvt_py, rvt.vis.hillshade

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


class RVTHillshade:
    def __init__(self):
        self.name = "RVT hillshade"
        self.description = "Calculates hillshade."
        # default values
        self.azimuth = 315.
        self.elevation = 35.
        self.padding = 1
        # 8bit (bytscale) parameters
        self.calc_8_bit = False
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
                'description': "Input raster for which to create the hillshade map."
            },
            {
                'name': 'calc_8_bit',
                'dataType': 'boolean',
                'value': self.calc_8_bit,
                'required': False,
                'displayName': "Calculate 8-bit",
                'description': "If True it returns 8-bit raster (0-255)."
            },
            {
                'name': 'sun_azimuth',
                'dataType': 'numeric',
                'value': self.azimuth,
                'required': False,
                'displayName': "Sun azimuth",
                'description': "Solar azimuth angle (clockwise from North) in degrees."
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
        self.prepare(azimuth=scalars.get('sun_azimuth'), elevation=scalars.get("sun_elevation"),
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
        kwargs['output_info']['bandCount'] = 1
        r = kwargs['raster_info']
        kwargs['output_info']['noData'] = np.nan
        if not self.calc_8_bit:
            kwargs['output_info']['pixelType'] = 'f4'
        else:
            kwargs['output_info']['pixelType'] = 'u1'
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['statistics'] = ()
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        dem = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)[0]  # Input pixel array.
        pixel_size = props['cellSize']
        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]

        hillshade = rvt.vis.hillshade(dem=dem, resolution_x=pixel_size[0],
                                      resolution_y=pixel_size[1], sun_azimuth=self.azimuth,
                                      sun_elevation=self.elevation, no_data=no_data, fill_no_data=False,
                                      keep_original_no_data=False)
        hillshade = hillshade[self.padding:-self.padding, self.padding:-self.padding]  # remove padding
        if self.calc_8_bit:
            hillshade = rvt.blend_func.normalize_image(visualization="hillshade", image=hillshade,
                                                       min_norm=self.min_bytscl, max_norm=self.max_bytscl,
                                                       normalization=self.mode_bytscl)
            hillshade = rvt.vis.byte_scale(data=hillshade, no_data=no_data)

        pixelBlocks['output_pixels'] = hillshade.astype(props['pixelType'], copy=False)

        # release memory
        del dem
        del hillshade
        gc.collect()

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = 'HS_A{}_H{}'.format(self.azimuth, self.elevation)
            if self.calc_8_bit:
                keyMetadata['datatype'] = 'Processed'
                name += "_8bit"
            else:
                keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, azimuth=315, elevation=35, calc_8_bit=False):
        self.azimuth = float(azimuth)
        self.elevation = float(elevation)
        self.calc_8_bit = calc_8_bit
