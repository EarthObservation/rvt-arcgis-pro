"""
Relief Visualization Toolbox – Visualization Functions

RVT normalize esri raster function
rvt_py, rvt.blend_func.normalize_image

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
import rvt.blend_func


class RVTNormalize:
    def __init__(self):
        self.name = "RVT normalize"
        self.description = "Normalize image (0-1)."
        # default values
        self.visualization = "Other"
        self.minimum = 0.
        self.maximum = 1.
        self.normalization = "value"

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "Input raster which we normalize."
            },
            {
                'name': 'visualization',
                'dataType': 'string',
                'value': self.visualization,
                'required': False,
                'displayName': "Visualization",
                'domain': ('Other', 'Slope gradient', 'Hillshade', 'Multiple directions hillshade', 'Sky-view factor',
                           'Anisotropic Sky-view factor', 'Openness - positive', 'Openness - negative',
                           'Sky illumination', 'Local dominance'),
                'description': "Visualization method."
            },
            {
                'name': 'minimum',
                'dataType': 'numeric',
                'value': self.minimum,
                'required': True,
                'displayName': "Minimum",
                'description': "Minimum cutoff in value or percent (normalization)."
            },
            {
                'name': 'maximum',
                'dataType': 'numeric',
                'value': self.maximum,
                'required': True,
                'displayName': "Maximum",
                'description': "Maximum cutoff in value or percent (normalization)."
            },
            {
                'name': 'normalization',
                'dataType': 'string',
                'value': self.normalization,
                'required': False,
                'displayName': "Normalization",
                'domain': ('value', 'perc'),
                'description': "Define minimum and maximum units. If value cutoff value if perc cutoff percent."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(visualization=scalars.get('visualization'), minimum=scalars.get("minimum"),
                     maximum=scalars.get("maximum"), normalization=scalars.get("normalization"))
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
        kwargs['output_info']['pixelType'] = 'f4'
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

        normalized_raster = rvt.blend_func.normalize_image(visualization=self.visualization,
                                                           image=dem, min_norm=self.minimum, max_norm=self.maximum,
                                                           normalization=self.normalization)

        pixelBlocks['output_pixels'] = normalized_raster.astype(props['pixelType'], copy=False)

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = 'NORM_M{}-{}_N{}'.format(self.minimum, self.maximum, self.normalization)
            keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, visualization="Other", minimum=0, maximum=1, normalization="value"):
        self.visualization = visualization
        self.minimum = float(minimum)
        self.maximum = float(maximum)
        self.normalization = normalization
