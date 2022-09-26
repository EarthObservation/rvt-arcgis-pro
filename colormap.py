"""
Relief Visualization Toolbox – Visualization Functions

RVT colormap (colorize) esri raster function
rvt_py, rvt.blend_func.gray_scale_to_color_ramp

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


class RVTColormap:
    def __init__(self):
        self.name = "RVT colormap"
        self.description = "Apply colormap on grayscale image."
        # default values
        self.colormap = "Reds_r"
        self.min_colormap_cut = 0.0
        self.max_colormap_cut = 1.0
        self.calc_8_bit = False

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input normalized Raster",
                'description': "Input normalized raster on which we apply colormap."
            },
            {
                'name': 'colormap',
                'dataType': 'string',
                'value': self.colormap,
                'required': True,
                'displayName': "Colormap",
                'domain': ('Reds', 'Reds_r', 'Greys', 'Greys_r', 'Purples', 'Purples_r', 'Blues', 'Blues_r',
                           'Greens', 'Greens_r', 'Oranges', 'Oranges_r',
                           'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'OrRd', 'OrRd_r', 'PuRd', 'PuRd_r',
                           'RdPu', 'RdPu_r', 'BuPu', 'BuPu_r', 'GnBu',
                           'GnBu_r', 'PuBu', 'PuBu_r', 'YlGnBu', 'YlGnBu_r', 'PuBuGn', 'PuBuGn_r',
                           'BuGn', 'BuGn_r', 'YlGn', 'YlGn_r', 'RdBu', 'RdBu_r', 'RdYlBu', 'RdYlBu_r',
                           'RdYlGn', 'RdYlGn_r', 'Spectral', 'Spectral_r', 'coolwarm', 'coolwarm_r'),
                'description': "Matplotlib colormap."
            },
            {
                'name': 'min_colormap_cut',
                'dataType': 'numeric',
                'value': self.min_colormap_cut,
                'required': True,
                'displayName': "Minimum colormap cut",
                'description': "What lower part of colormap to cut to select part of colormap. "
                               "Valid values are between 0 and 1, if 0.2 it cuts off (deletes)"
                               " 20% of lower colors in colormap."
            },
            {
                'name': 'max_colormap_cut',
                'dataType': 'numeric',
                'value': self.max_colormap_cut,
                'required': True,
                'displayName': "Maximum colormap cut",
                'description': "What upper part of colormap to cut to select part of colormap. "
                               "Valid values are between 0 and 1, if 0.8 it cuts off (deletes)"
                               " 20% of upper colors in colormap."
            },
            {
                'name': 'calc_8_bit',
                'dataType': 'boolean',
                'value': self.calc_8_bit,
                'required': False,
                'displayName': "Calculate 8-bit",
                'description': "If True it returns 8-bit raster (0-255)."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(colormap=scalars.get('colormap'), min_colormap_cut=scalars.get("min_colormap_cut"),
                     max_colormap_cut=scalars.get("max_colormap_cut"), calc_8_bit=scalars.get("calc_8_bit"))
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
        kwargs['output_info']['bandCount'] = 3
        r = kwargs['raster_info']
        kwargs['output_info']['noData'] = np.nan
        if not self.calc_8_bit:
            kwargs['output_info']['pixelType'] = 'f4'
        else:
            kwargs['output_info']['pixelType'] = 'u1'
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        norm_image = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)[0]  # Input pixel array.
        pixel_size = props['cellSize']
        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")

        colored_raster = rvt.blend_func.gray_scale_to_color_ramp(gray_scale=norm_image, colormap=self.colormap,
                                                                 min_colormap_cut=self.min_colormap_cut,
                                                                 max_colormap_cut=self.max_colormap_cut,
                                                                 output_8bit=self.calc_8_bit)

        pixelBlocks['output_pixels'] = colored_raster.astype(props['pixelType'], copy=False)

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = 'Cmap_{}_M{}-{}'.format(self.colormap, self.min_colormap_cut, self.max_colormap_cut)
            if self.calc_8_bit:
                keyMetadata['datatype'] = 'Processed'
                name += "_8bit"
            else:
                keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, colormap="Reds_r", min_colormap_cut=0, max_colormap_cut=1, calc_8_bit=False):
        self.colormap = colormap
        self.min_colormap_cut = float(min_colormap_cut)
        self.max_colormap_cut = float(max_colormap_cut)
        self.calc_8_bit = calc_8_bit
