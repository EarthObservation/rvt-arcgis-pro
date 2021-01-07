"""
NAME:
    RVT local dominance esri raster function
    rvt_py, rvt.vis.local_dominance

PROJECT MANAGER:
    Žiga Kokalj (ziga.kokalj@zrc-sazu.si)

AUTHORS:
    Klemen Zakšek
    Krištof Oštir
    Klemen Čotar
    Maja Somrak
    Žiga Maroh

COPYRIGHT:
    Research Centre of the Slovenian Academy of Sciences and Arts
    University of Ljubljana, Faculty of Civil and Geodetic Engineering
"""

import numpy as np
import rvt.vis


class RVTLocalDominance:
    def __init__(self):
        self.name = "RVT Local dominance"
        self.description = "Calculates Local dominance."
        # default values
        self.min_rad = 10.
        self.max_rad = 20.
        self.rad_inc = 1.
        self.anglr_res = 15.
        self.observer_h = 1.7
        self.padding = int(self.max_rad/2)
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
                'description': "Input raster for which to create the local dominance map."
            },
            {
                'name': 'min_rad',
                'dataType': 'numeric',
                'value': self.min_rad,
                'required': False,
                'displayName': "Minimum radial distance",
                'description': "Minimum radial distance (in pixels) at which the algorithm starts with visualization"
                               " computation."
            },
            {
                'name': 'max_rad',
                'dataType': 'numeric',
                'value': self.max_rad,
                'required': False,
                'displayName': "Maximum radial distance",
                'description': "Maximum radial distance (in pixels) at which the algorithm ends with visualization"
                               " computation."
            },
            {
                'name': 'rad_inc',
                'dataType': 'numeric',
                'value': self.rad_inc,
                'required': False,
                'displayName': "Radial distance steps",
                'description': "Radial distance steps in pixels"
            },
            {
                'name': 'anglr_res',
                'dataType': 'numeric',
                'value': self.anglr_res,
                'required': False,
                'displayName': "Angular resolution",
                'description': "Angular step for determination of number of angular directions."
            },
            {
                'name': 'observer_h',
                'dataType': 'numeric',
                'value': self.observer_h,
                'required': False,
                'displayName': "Observer height",
                'description': "Height at which we observe the terrain in meters."
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
        self.prepare(min_rad=scalars.get('min_rad'), max_rad=scalars.get("max_rad"), rad_inc=scalars.get("rad_inc"),
                     anglr_res=scalars.get("anglr_res"), observer_h=scalars.get("observer_h"),
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

        local_dominance = rvt.vis.local_dominance(dem=dem, min_rad=self.min_rad, max_rad=self.max_rad,
                                                  rad_inc=self.rad_inc, angular_res=self.anglr_res,
                                                  observer_height=self.observer_h, no_data=no_data,
                                                  fill_no_data=self.fill_no_data,
                                                  keep_original_no_data=self.keep_original_no_data)
        local_dominance = local_dominance[self.padding:-self.padding, self.padding:-self.padding ]  # remove padding
        pixelBlocks['output_pixels'] = local_dominance.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def prepare(self, min_rad=10, max_rad=20, rad_inc=1, anglr_res=15, observer_h=1.7, fill_no_data=True,
                keep_original_no_data=False):
        self.min_rad = int(min_rad)
        self.max_rad = int(max_rad)
        self.rad_inc = int(rad_inc)
        self.anglr_res = int(anglr_res)
        self.observer_h = float(observer_h)
        self.padding = int(max_rad/2)
        self.fill_no_data = fill_no_data
        self.keep_original_no_data = keep_original_no_data
