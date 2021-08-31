"""
Relief Visualization Toolbox – Visualization Functions

RVT multi-scale relief model
rvt_py, rvt.vis.msrm

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


class RVTMsrm:
    def __init__(self):
        self.name = "RVT msrm"
        self.description = "Calculates Multi-scale relief model."
        # default values
        self.feature_min = 0.
        self.feature_max = 20.
        self.scaling_factor = 2.
        self.padding = 1
        # 8bit (bytscale) parameters
        self.calc_8_bit = False
        self.mode_bytscl = "percent"
        self.min_bytscl = 2
        self.max_bytscl = 2

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "Input raster for which to create the Multi-scale relief model."
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
                'name': 'feature_min',
                'dataType': 'numeric',
                'value': self.feature_min,
                'required': True,
                'displayName': "Feature minimum",
                'description': "Minimum size of the feature you want to detect in meters."
            },
            {
                'name': 'feature_max',
                'dataType': 'numeric',
                'value': self.feature_max,
                'required': True,
                'displayName': "Feature maximum",
                'description': "Maximum size of the feature you want to detect in meters."
            },
            {
                'name': 'scaling_factor',
                'dataType': 'numeric',
                'value': self.scaling_factor,
                'required': True,
                'displayName': "Scaling factor",
                'description': "Scaling factor, if larger than 1 it provides larger range of MSRM values"
                               " (increase contrast and visibility), but could result in a loss of sensitivity"
                               " for intermediate sized features."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(feature_min=scalars.get("feature_min"), feature_max=scalars.get("feature_max"),
                     scaling_factor=scalars.get("scaling_factor"), calc_8_bit=scalars.get("calc_8_bit"))
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

        msrm = rvt.vis.msrm(dem=dem, resolution=pixel_size[0], feature_min=self.feature_min,
                            feature_max=self.feature_max, scaling_factor=self.scaling_factor,
                            no_data=no_data, fill_no_data=False, keep_original_no_data=False)
        msrm = msrm[self.padding:-self.padding, self.padding:-self.padding]
        if self.calc_8_bit:
            msrm = rvt.blend_func.normalize_image(visualization="multi-scale relief model", image=msrm,
                                                  min_norm=self.min_bytscl, max_norm=self.max_bytscl,
                                                  normalization=self.mode_bytscl)
            msrm = rvt.vis.byte_scale(data=msrm, no_data=no_data)

        pixelBlocks['output_pixels'] = msrm.astype(props['pixelType'], copy=False)

        # release memory
        del dem
        del pixel_size
        del no_data
        del msrm
        gc.collect()

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = 'MSRM_F_M{}-{}_S{}'.format(self.feature_min, self.feature_max, self.scaling_factor)
            if self.calc_8_bit:
                keyMetadata['datatype'] = 'Processed'
                name += "_8bit"
            else:
                keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, feature_min=1, feature_max=5, scaling_factor=3, calc_8_bit=False):
        self.feature_min = float(feature_min)
        self.feature_max = float(feature_max)
        self.scaling_factor = int(scaling_factor)
        resolution = 1  # we can't get resolution in getConfiguration so we will set it to 1
        n = int(np.ceil(((self.feature_max - resolution) / (2 * resolution)) ** (1 / self.scaling_factor)))
        self.padding = n ** self.scaling_factor
        self.calc_8_bit = calc_8_bit


def change_0_pad_to_edge_pad(dem, pad_width):
    if np.any(dem[0:pad_width, :]) or np.any(dem[-pad_width:, :]) or\
            np.any(dem[:, 0:pad_width]) or np.any(dem[:, -pad_width:]):
        return dem
    dem = dem[pad_width:-pad_width, pad_width:-pad_width]  # remove esri 0 padding
    dem = np.pad(array=dem, pad_width=pad_width, mode="edge")  # add new edge padding
    return dem
