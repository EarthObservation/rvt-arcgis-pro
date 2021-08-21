"""
NAME:
    RVT Anisotropic Sky-view factor esri raster function
    rvt_py, rvt.vis.sky_view_factor

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
        self.padding = int(self.max_rad)
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
                'description': "Input raster for which to create the sky-view factor map."
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
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(nr_directions=scalars.get('nr_directions'), max_rad=scalars.get("max_rad"),
                     noise=scalars.get("noise_remove"), level=scalars.get("level"), direction=scalars.get("direction"),
                     calc_8_bit=scalars.get("calc_8_bit"))
        return {
            'compositeRasters': False,
            'inheritProperties': 2 | 4 | 8,
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
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]

        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")

        dict_asvf = rvt.vis.sky_view_factor(dem=dem, resolution=pixel_size[0], compute_svf=False, compute_asvf=True,
                                            compute_opns=False, svf_n_dir=self.nr_directions, svf_r_max=self.max_rad,
                                            svf_noise=self.noise, asvf_level=self.level, asvf_dir=self.direction,
                                            no_data=no_data, fill_no_data=False,
                                            keep_original_no_data=False)
        asvf = dict_asvf["asvf"][self.padding:-self.padding, self.padding:-self.padding]  # remove padding
        if self.calc_8_bit:
            asvf = rvt.blend_func.normalize_image(visualization="anisotropic sky-view factor", image=asvf,
                                                  min_norm=self.min_bytscl, max_norm=self.max_bytscl,
                                                  normalization=self.mode_bytscl)
            asvf = rvt.vis.byte_scale(data=asvf, no_data=no_data)

        pixelBlocks['output_pixels'] = asvf.astype(props['pixelType'], copy=False)

        # release memory
        del dem
        del pixel_size
        del no_data
        del dict_asvf
        del asvf
        gc.collect()

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = "SVF-A_R{}_D{}_A{}".format(self.max_rad, self.nr_directions, self.direction)
            if self.level == 1:
                name += "_ALlow"
            elif self.level == 2:
                name += "_ALstrong"

            if self.calc_8_bit:
                keyMetadata['datatype'] = 'Processed'
                name += "_8bit"
            else:
                keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, nr_directions=16, max_rad=10, noise="0", direction=315, level="1", calc_8_bit=False):
        self.nr_directions = int(nr_directions)
        self.max_rad = int(max_rad)
        self.noise = int(noise[0])
        self.direction = int(direction)
        self.level = int(level[0])
        self.calc_8_bit = bool(calc_8_bit)
        self.padding = int(max_rad)


def change_0_pad_to_edge_pad(dem, pad_width):
    dem = dem[pad_width:-pad_width, pad_width:-pad_width]  # remove esri 0 padding
    dem = np.pad(array=dem, pad_width=pad_width, mode="edge")  # add new edge padding
    return dem
