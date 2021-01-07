"""
Relief Visualization Toolbox – Visualization Functions

RVT Positive/Negative Openness esri raster function
rvt_py, rvt.vis.sky_view_factor

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


class RVTOpenness:
    def __init__(self):
        self.name = "RVT Openness"
        self.description = "Calculates Openness."
        # default values
        self.nr_directions = 16.
        self.max_rad = 10.
        self.noise = "0-don't remove"
        self.pos_neg = "Positive"
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
                'description': "Input raster for which to create the sky-view factor map."
            },
            {
                'name': 'nr_directions',
                'dataType': 'numeric',
                'value': self.nr_directions,
                'required': False,
                'displayName': "Number of directions",
                'description': "Number of directions."
            },
            {
                'name': 'max_rad',
                'dataType': 'numeric',
                'value': self.max_rad,
                'required': False,
                'displayName': "Max radius",
                'description': "Maximal search radius in pixels."
            },
            {
                'name': 'noise_remove',
                'dataType': 'string',
                'value': self.noise,
                'required': False,
                'displayName': "Noise removal",
                'domain': ("0-don't remove", "1-low", "2-med", "3-high"),
                'description': "The level of noise remove (0-don't remove, 1-low, 2-med, 3-high)."
            },
            {
                'name': 'pos_neg',
                'dataType': 'string',
                'value': self.pos_neg,
                'required': False,
                'displayName': "Positive / Negative",
                'domain': ("Positive", "Negative"),
                'description': "Which one to calculate (negative openness is openness where dem is negative, "
                               "multiplied with -1))."
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
        self.prepare(nr_directions=scalars.get('nr_directions'), max_rad=scalars.get("max_rad"),
                     noise=scalars.get("noise_remove"), pos_neg=scalars.get("pos_neg"),
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

        if self.pos_neg == "Negative":
            dem = -1 * dem

        dict_opns = rvt.vis.sky_view_factor(dem=dem, resolution=pixel_size[0], compute_svf=False, compute_asvf=False,
                                            compute_opns=True, svf_n_dir=self.nr_directions, svf_r_max=self.max_rad,
                                            svf_noise=self.noise, no_data=no_data, fill_no_data=self.fill_no_data,
                                            keep_original_no_data=self.keep_original_no_data)
        opns = dict_opns["opns"][self.padding:-self.padding, self.padding:-self.padding]

        pixelBlocks['output_pixels'] = opns.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def prepare(self, nr_directions=16, max_rad=10, noise="0", pos_neg="Positive", fill_no_data=True,
                keep_original_no_data=False):
        self.nr_directions = int(nr_directions)
        self.max_rad = int(max_rad)
        self.noise = int(noise[0])
        self.pos_neg = pos_neg
        self.padding = int(max_rad/2)
        self.fill_no_data = fill_no_data
        self.keep_original_no_data = keep_original_no_data
