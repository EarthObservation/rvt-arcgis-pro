"""
Relief Visualization Toolbox – Visualization Functions

RVT Convert to 8bit esri raster function
rvt_py, rvt.vis.byte_scale

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


class RVTto8Bit:
    def __init__(self):
        self.name = "RVT Convert to 8bit"
        self.description = "Convert image values 0-255 (Byte scale)."

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "Input raster to convert to 8bit."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare()  # nothing to prepare
        return {
            'compositeRasters': False,
            'inheritProperties': 4,
            'invalidateProperties': 2 | 4 | 8,
            'inputMask': False,
            'resampling': False,
            'padding': 0,
            'resamplingType': 1
        }

    def updateRasterInfo(self, **kwargs):
        r = kwargs['raster_info']
        if int(r['bandCount']) == 3:
            kwargs['output_info']['bandCount'] = 3
        else:
            kwargs['output_info']['bandCount'] = 1
        kwargs['output_info']['noData'] = np.nan
        kwargs['output_info']['pixelType'] = 'u1'
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['statistics'] = ()
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        dem = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)  # Input pixel array.
        if dem.shape[0] == 1:
            dem = dem[0]
        pixel_size = props['cellSize']
        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")

        bytescl_raster = rvt.vis.byte_scale(data=dem)

        pixelBlocks['output_pixels'] = bytescl_raster.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            keyMetadata['datatype'] = 'Processed'
            keyMetadata['productname'] = 'RVT 8-bit'
        return keyMetadata

    def prepare(self):
        pass
