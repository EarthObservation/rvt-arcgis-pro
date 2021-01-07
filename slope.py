"""
Relief Visualization Toolbox – Visualization Functions

RVT slope esri raster function
rvt_py, rvt.vis.slope

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


class RVTSlope:
    def __init__(self):
        self.name = "RVT slope"
        self.description = "Calculates slope(gradient)."
        # default values
        self.ve_factor = 1.
        self.output_unit = "degree"
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
                'description': "Input raster for which to create the slope map."
            },
            {
                'name': 've_factor',
                'dataType': 'numeric',
                'value': self.ve_factor,
                'required': False,
                'displayName': "Ve-factor",
                'description': ("Vertical exaggeration factor (must be greater than 0).")
            },
            {
                'name': 'output_unit',
                'dataType': 'string',
                'value': self.output_unit,
                'required': False,
                'displayName': "Output unit",
                'domain': ('degree', 'radian', 'percent'),
                'description': ("Unit of the output raster.")
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
        self.prepare(ve_factor=scalars.get('ve_factor'), output_unit=scalars.get("output_unit"),
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
        ###  COPY INTO CODE AND UNCOMMENT IT
        import pickle
        import os

        debug_logs_directory = r'D:\RVT_py\debug'
        fname = 'debug.txt'
        filename = os.path.join(debug_logs_directory, fname)
        pix_array = props["noData"]
        pickle.dump(pix_array, open(filename, "wb"))
        ###
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]
        else:  # if no data is None we can't fill no data
            self.fill_no_data = False
            self.keep_original_no_data = False

        dict_slp_asp = rvt.vis.slope_aspect(dem=dem, resolution_x=pixel_size[0], resolution_y=pixel_size[1],
                                            ve_factor=self.ve_factor, output_units=self.output_unit, no_data=no_data,
                                            fill_no_data=self.fill_no_data,
                                            keep_original_no_data=self.keep_original_no_data)
        slope = dict_slp_asp["slope"][self.padding:-self.padding, self.padding:-self.padding]
        pixelBlocks['output_pixels'] = slope.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def prepare(self, ve_factor=315, output_unit=35, fill_no_data=True, keep_original_no_data=False):
        self.ve_factor = ve_factor
        self.output_unit = output_unit
        self.fill_no_data = fill_no_data
        self.keep_original_no_data = keep_original_no_data
