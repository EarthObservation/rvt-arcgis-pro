"""
Relief Visualization Toolbox – Visualization Functions

RVT simple local relief model esri raster function
rvt_py, rvt.vis.slrm

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


class RVTSlrm:
    def __init__(self):
        self.name = "RVT simple local relief model."
        self.description = "Calculates simple local relief model."
        # default values
        self.radius_cell = 20.
        self.padding = int(self.radius_cell)
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
                'description': "Input raster for which to create the simple local relief model."
            },
            {
                'name': 'radius_cell',
                'dataType': 'numeric',
                'value': self.radius_cell,
                'required': False,
                'displayName': "Radius cell",
                'description': "Radius for trend assessment [pixels]."
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
        self.prepare(radius_cell=scalars.get('radius_cell'), fill_no_data=scalars.get("fill_no_data"),
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
        dem = change_0_pad_to_edge_pad(dem=dem, pad_width=self.padding)  # change padding
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]
        else:  # if no data is None we can't fill no data
            self.fill_no_data = False
            self.keep_original_no_data = False

        slrm = rvt.vis.slrm(dem=dem, radius_cell=self.radius_cell, no_data=no_data, fill_no_data=self.fill_no_data,
                            keep_original_no_data=self.keep_original_no_data)
        slrm = slrm[self.padding:-self.padding, self.padding:-self.padding]
        pixelBlocks['output_pixels'] = slrm.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def prepare(self, radius_cell=20, fill_no_data=True, keep_original_no_data=False):
        self.radius_cell = int(radius_cell)
        self.padding = int(radius_cell)
        self.fill_no_data = fill_no_data
        self.keep_original_no_data = keep_original_no_data


def change_0_pad_to_edge_pad(dem, pad_width):
    dem = dem[pad_width:-pad_width, pad_width:-pad_width]  # remove esri 0 padding
    dem = np.pad(array=dem, pad_width=pad_width, mode="edge")  # add new edge padding
    return dem
