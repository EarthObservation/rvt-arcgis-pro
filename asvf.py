"""
NAME:
    RVT Anisotropic Sky-view factor esri raster function
    rvt_py, rvt.vis.sky_view_factor

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


class RVTASvf:
    def __init__(self):
        self.name = "RVT Anisotropic Sky-view factor"
        self.description = "Calculates Anisotropic Sky-view factor."
        # default values
        self.nr_directions = 16.
        self.max_rad = 10.
        self.noise = "0-don't remove"  # in prepare changed to int
        self.level = "1-low"  # in prepare changed to int
        self.direction = 315.
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
                'name': 'direction',
                'dataType': 'numeric',
                'value': self.direction,
                'required': False,
                'displayName': "Anisotropy direction",
                'description': "Main direction of anisotropy."
            },
            {
                'name': 'level',
                'dataType': 'string',
                'value': self.level,
                'required': False,
                'displayName': "Level of anisotropy",
                'domain': ("1-low", "2-high"),
                'description': "The level of anisotropy (1-low, 2-high)."
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
                     noise=scalars.get("noise_remove"), level=scalars.get("level"), direction=scalars.get("direction"),
                     fill_no_data=scalars.get("fill_no_data"),
                     keep_original_no_data=scalars.get("keep_original_no_data"))
        return {
            'compositeRasters': False,
            'inheritProperties': 2 | 4 | 8,
            'invalidateProperties': 2 | 4 | 8,
            'inputMask': False,
            'resampling': False,
            'padding': self.padding
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
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]
        else:  # if no data is None we can't fill no data
            self.fill_no_data = False
            self.keep_original_no_data = False

        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")

        dict_asvf = rvt.vis.sky_view_factor(dem=dem, resolution=pixel_size[0], compute_svf=False, compute_asvf=True,
                                            compute_opns=False, svf_n_dir=self.nr_directions, svf_r_max=self.max_rad,
                                            svf_noise=self.noise, asvf_level=self.level, asvf_dir=self.direction,
                                            no_data=no_data, fill_no_data=self.fill_no_data,
                                            keep_original_no_data=self.keep_original_no_data)
        asvf = dict_asvf["asvf"][self.padding:-self.padding, self.padding:-self.padding]  # remove padding
        pixelBlocks['output_pixels'] = asvf.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def prepare(self, nr_directions=16, max_rad=10, noise="0", direction=315, level="1", fill_no_data=True,
                keep_original_no_data=False):
        self.nr_directions = int(nr_directions)
        self.max_rad = int(max_rad)
        self.noise = int(noise[0])
        self.direction = int(direction)
        self.level = int(level[0])
        self.padding = int(max_rad/2)
        self.fill_no_data = fill_no_data
        self.keep_original_no_data = keep_original_no_data