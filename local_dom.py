"""
NAME:
    RVT local dominance esri raster function
    rvt_py, rvt.vis.local_dominance

PROJECT MANAGER:
    Žiga Kokalj (ziga.kokalj@zrc-sazu.si)

Credits:
    Žiga Kokalj (ziga.kokalj@zrc-sazu.si)
    Krištof Oštir (kristof.ostir@fgg.uni-lj.si)
    Klemen Zakšek
    Peter Pehani
    Klemen Čotar
    Maja Somrak
    Žiga Maroh

COPYRIGHT:
    Research Centre of the Slovenian Academy of Sciences and Arts
    University of Ljubljana, Faculty of Civil and Geodetic Engineering
"""

import numpy as np
import rvt.vis
import rvt.blend_func
import gc


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
        self.padding = int(self.max_rad)
        # 8bit (bytscale) parameters
        self.calc_8_bit = False
        self.mode_bytscl = "value"
        self.min_bytscl = 0.5
        self.max_bytscl = 1.8

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
                'name': 'calc_8_bit',
                'dataType': 'boolean',
                'value': self.calc_8_bit,
                'required': False,
                'displayName': "Calculate 8-bit",
                'description': "If True it returns 8-bit raster (0-255)."
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
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(min_rad=scalars.get('min_rad'), max_rad=scalars.get("max_rad"), rad_inc=scalars.get("rad_inc"),
                     anglr_res=scalars.get("anglr_res"), observer_h=scalars.get("observer_h"),
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
        dem = change_0_pad_to_edge_pad(dem, self.padding)
        pixel_size = props['cellSize']
        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]

        local_dominance = rvt.vis.local_dominance(dem=dem, min_rad=self.min_rad, max_rad=self.max_rad,
                                                  rad_inc=self.rad_inc, angular_res=self.anglr_res,
                                                  observer_height=self.observer_h, no_data=no_data,
                                                  fill_no_data=False,
                                                  keep_original_no_data=False)
        local_dominance = local_dominance[self.padding:-self.padding, self.padding:-self.padding]  # remove padding
        if self.calc_8_bit:
            local_dominance = rvt.blend_func.normalize_image(visualization="local dominance", image=local_dominance,
                                                             min_norm=self.min_bytscl, max_norm=self.max_bytscl,
                                                             normalization=self.mode_bytscl)
            local_dominance = rvt.vis.byte_scale(data=local_dominance, no_data=no_data)

        pixelBlocks['output_pixels'] = local_dominance.astype(props['pixelType'], copy=False)

        # release memory
        del dem
        del pixel_size
        del no_data
        del local_dominance
        gc.collect()

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = 'LD_R_M{}-{}_DI{}_A{}_OH{}'.format(self.min_rad, self.max_rad,
                                                      self.rad_inc, self.anglr_res,
                                                      self.observer_h)
            if self.calc_8_bit:
                keyMetadata['datatype'] = 'Processed'
                name += "_8bit"
            else:
                keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, min_rad=10, max_rad=20, rad_inc=1, anglr_res=15, observer_h=1.7, calc_8_bit=False):
        self.min_rad = int(min_rad)
        self.max_rad = int(max_rad)
        self.rad_inc = int(rad_inc)
        self.anglr_res = int(anglr_res)
        self.observer_h = float(observer_h)
        self.padding = int(max_rad)
        self.calc_8_bit = calc_8_bit


def change_0_pad_to_edge_pad(dem, pad_width):
    dem = dem[pad_width:-pad_width, pad_width:-pad_width]  # remove esri 0 padding
    dem = np.pad(array=dem, pad_width=pad_width, mode="edge")  # add new edge padding
    return dem
