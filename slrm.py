"""
Relief Visualization Toolbox – Visualization Functions

RVT simple local relief model esri raster function
rvt_py, rvt.vis.slrm

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


class RVTSlrm:
    def __init__(self):
        self.name = "RVT simple local relief model."
        self.description = "Calculates simple local relief model."
        # default values
        self.radius_cell = 20.
        self.padding = int(self.radius_cell)
        # 8bit (bytscale) parameters
        self.calc_8_bit = False
        self.mode_bytscl = "value"
        self.min_bytscl = -2
        self.max_bytscl = 2

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
                'name': 'calc_8_bit',
                'dataType': 'boolean',
                'value': self.calc_8_bit,
                'required': False,
                'displayName': "Calculate 8-bit",
                'description': "If True it returns 8-bit raster (0-255)."
            },
            {
                'name': 'radius_cell',
                'dataType': 'numeric',
                'value': self.radius_cell,
                'required': False,
                'displayName': "Radius cell",
                'description': "Radius for trend assessment [pixels]."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(radius_cell=scalars.get('radius_cell'), calc_8_bit=scalars.get("calc_8_bit"))
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
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]

        slrm = rvt.vis.slrm(dem=dem, radius_cell=self.radius_cell, no_data=no_data, fill_no_data=False,
                            keep_original_no_data=False)
        slrm = slrm[self.padding:-self.padding, self.padding:-self.padding]
        if self.calc_8_bit:
            slrm = rvt.blend_func.normalize_image(visualization="simple local relief model", image=slrm,
                                                  min_norm=self.min_bytscl, max_norm=self.max_bytscl,
                                                  normalization=self.mode_bytscl)
            slrm = rvt.vis.byte_scale(data=slrm, no_data=no_data, c_min=0, c_max=1)

        pixelBlocks['output_pixels'] = slrm.astype(props['pixelType'], copy=False)

        # release memory
        del dem
        del no_data
        del slrm
        gc.collect()

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = 'SLRM_R{}'.format(self.radius_cell)
            if self.calc_8_bit:
                keyMetadata['datatype'] = 'Processed'
                name += "_8bit"
            else:
                keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, radius_cell=20, calc_8_bit=False):
        self.radius_cell = int(radius_cell)
        self.padding = int(radius_cell)
        self.calc_8_bit = calc_8_bit
