"""
Relief Visualization Toolbox – Visualization Functions

RVT hillshade esri raster function
rvt_py, rvt.vis.hillshade

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


class RVTHillshade:
    def __init__(self):
        self.name = "RVT hillshade"
        self.description = "Calculates hillshade."
        # default values
        self.azimuth = 315.
        self.elevation = 35.
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
                'description': "Input raster for which to create the hillshade map."
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
        self.prepare(azimuth=scalars.get('sun_azimuth'), elevation=scalars.get("sun_elevation"),
                     fill_no_data=scalars.get("fill_no_data"),
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
        kwargs['output_info']['bandCount'] = 1
        r = kwargs['raster_info']
        kwargs['output_info']['noData'] = np.nan
        kwargs['output_info']['pixelType'] = 'f4'
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
        else:  # if no data is None we can't fill no data
            self.fill_no_data = False
            self.keep_original_no_data = False

        hillshade = rvt.vis.hillshade(dem=dem, resolution_x=pixel_size[0],
                                      resolution_y=pixel_size[1], sun_azimuth=self.azimuth,
                                      sun_elevation=self.elevation, no_data=no_data, fill_no_data=self.fill_no_data,
                                      keep_original_no_data=self.keep_original_no_data)
        hillshade = hillshade[self.padding:-self.padding, self.padding:-self.padding]  # remove padding
        pixelBlocks['output_pixels'] = hillshade.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def prepare(self, azimuth=315, elevation=35, fill_no_data=True, keep_original_no_data=False):
        self.azimuth = azimuth
        self.elevation = elevation
        self.fill_no_data = fill_no_data
        self.keep_original_no_data = keep_original_no_data
