"""
Relief Visualization Toolbox – Visualization Functions

RVT blend esri raster function
rvt_py, rvt.blend_func.blend_images, rvt.blend_func.render_images

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
import rvt.vis


class RVTBlend:
    def __init__(self):
        self.name = "RVT blend"
        self.description = "Blend and render two images together."
        # default values
        self.blend_mode = "normal"
        self.opacity = 100.
        self.calc_8_bit = True

    def getParameterInfo(self):
        return [
            {
                'name': 'topraster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input top Raster",
                'description': "Input top raster on which we apply opacity, blend and render with background raster."
            },
            {
                'name': 'bgraster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input background Raster",
                'description': "Input background raster which we blend and render with top raster."
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
                'name': 'blend_mode',
                'dataType': 'string',
                'value': self.blend_mode,
                'required': True,
                'displayName': "Blend mode",
                'domain': ('normal', 'multiply', 'overlay', 'luminosity', 'screen', "soft_light"),
                'description': "Blending mode for blending top and background raster together."
            },
            {
                'name': 'opacity',
                'dataType': 'numeric',
                'value': self.opacity,
                'required': True,
                'displayName': "Opacity",
                'description': "Opacity in percent to apply on top raster (0-100)."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(blend_mode=scalars.get('blend_mode'), opacity=scalars.get("opacity"),
                     calc_8_bit=scalars.get("calc_8_bit"))
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
        t = kwargs['topraster_info']
        b = kwargs['bgraster_info']
        if int(t['bandCount']) == 3 or int(b['bandCount']) == 3:
            kwargs['output_info']['bandCount'] = 3
        else:
            kwargs['output_info']['bandCount'] = 1
        kwargs['output_info']['noData'] = np.nan
        if not self.calc_8_bit:
            kwargs['output_info']['pixelType'] = 'f4'
        else:
            kwargs['output_info']['pixelType'] = 'u1'
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        top_raster = np.array(pixelBlocks['topraster_pixels'], dtype='f4', copy=False)
        if top_raster.shape[0] == 1:
            top_raster = top_raster[0]
        background_raster = np.array(pixelBlocks['bgraster_pixels'], dtype='f4', copy=False)
        if background_raster.shape[0] == 1:
            background_raster = background_raster[0]
        pixel_size = props['cellSize']
        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")

        if np.nanmin(top_raster) < 0 or np.nanmax(top_raster) > 1:
            top_raster = rvt.blend_func.scale_0_to_1(top_raster)
        if np.nanmin(background_raster) < 0 or np.nanmax(background_raster) > 1:
            background_raster = rvt.blend_func.scale_0_to_1(background_raster)

        top_raster = rvt.blend_func.blend_images(blend_mode=self.blend_mode, active=top_raster,
                                                 background=background_raster)
        rendered_image = rvt.blend_func.render_images(active=top_raster, background=background_raster,
                                                      opacity=self.opacity)
        if self.calc_8_bit:
            rendered_image = rvt.vis.byte_scale(data=rendered_image, c_min=0.0, c_max=1.0)

        pixelBlocks['output_pixels'] = rendered_image.astype(props['pixelType'], copy=False)

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = 'BLEND_M{}_O{}'.format(self.blend_mode, self.opacity)
            if self.calc_8_bit:
                keyMetadata['datatype'] = 'Processed'
                name += "_8bit"
            else:
                keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, blend_mode="normal", opacity=100, calc_8_bit=False):
        opacity = int(opacity)
        self.blend_mode = blend_mode
        self.calc_8_bit = calc_8_bit
        if opacity > 100:
            self.opacity = 100
        elif opacity < 0:
            self.opacity = 0
        else:
            self.opacity = opacity
