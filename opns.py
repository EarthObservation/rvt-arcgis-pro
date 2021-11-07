"""
Relief Visualization Toolbox – Visualization Functions

RVT Positive/Negative Openness esri raster function
rvt_py, rvt.vis.sky_view_factor

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


class RVTOpenness:
    def __init__(self):
        self.name = "RVT Openness"
        self.description = "Calculates Openness."
        # default values
        self.nr_directions = 16.
        self.max_rad = 10.
        self.noise = "0-don't remove"
        self.pos_neg = "Positive"
        self.padding = int(self.max_rad)
        # 8bit (bytscale) parameters
        self.calc_8_bit = False
        self.mode_bytscl = "value"
        self.min_bytscl = 60
        self.max_bytscl = 95

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
                'name': 'pos_neg',
                'dataType': 'string',
                'value': self.pos_neg,
                'required': False,
                'displayName': "Positive / Negative",
                'domain': ("Positive", "Negative"),
                'description': "Which one to calculate (negative openness is openness where dem is negative, "
                               "multiplied with -1))."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(nr_directions=scalars.get('nr_directions'), max_rad=scalars.get("max_rad"),
                     noise=scalars.get("noise_remove"), pos_neg=scalars.get("pos_neg"),
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
        # dem = change_0_pad_to_edge_pad(dem, self.padding)
        pixel_size = props['cellSize']
        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]

        if self.pos_neg == "Negative":
            dem = -1 * dem

        dict_opns = rvt.vis.sky_view_factor(dem=dem, resolution=pixel_size[0], compute_svf=False, compute_asvf=False,
                                            compute_opns=True, svf_n_dir=self.nr_directions, svf_r_max=self.max_rad,
                                            svf_noise=self.noise, no_data=no_data)
        opns = dict_opns["opns"][self.padding:-self.padding, self.padding:-self.padding]
        if self.calc_8_bit:
            visualization = "openness - positive"
            if self.pos_neg == "Negative":
                visualization = "openness - negative"
            opns = rvt.blend_func.normalize_image(visualization=visualization, image=opns,
                                                  min_norm=self.min_bytscl, max_norm=self.max_bytscl,
                                                  normalization=self.mode_bytscl)
            opns = rvt.vis.byte_scale(data=opns, no_data=no_data)

        pixelBlocks['output_pixels'] = opns.astype(props['pixelType'], copy=False)

        # release memory
        del dem
        del pixel_size
        del no_data
        del dict_opns
        del opns
        gc.collect()

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name_pos_neg = "NEG"
            if self.pos_neg == "Positive":
                 name_pos_neg = "POS"
            name = 'OPEN-{}_R{}_D{}'.format(name_pos_neg, self.max_rad, self.nr_directions)
            if self.calc_8_bit:
                keyMetadata['datatype'] = 'Processed'
                name += "_8bit"
            else:
                keyMetadata['datatype'] = 'Generic'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, nr_directions=16, max_rad=10, noise="0", pos_neg="Positive", calc_8_bit=False):
        self.nr_directions = int(nr_directions)
        self.max_rad = int(max_rad)
        self.noise = int(noise[0])
        self.pos_neg = pos_neg
        self.padding = int(max_rad)
        self.calc_8_bit = calc_8_bit


def change_0_pad_to_edge_pad(dem, pad_width):
    dem_out = dem.copy()
    if not np.any(dem[:pad_width, :]):  # if all top padding zeros
        dem_out = dem_out[pad_width:, :]  # remove esri 0 padding top
        # pad top
        dem_out = np.pad(array=dem_out, pad_width=((pad_width,0), (0,0)), mode="edge")
    if not np.any(dem[-pad_width:, :]):  # if all bottom padding zeros
        dem_out = dem_out[:-pad_width, :]  # remove esri 0 padding bottom
        # pad bottom
        dem_out = np.pad(array=dem_out, pad_width=((0, pad_width), (0, 0)), mode="edge")
    if not np.any(dem[:, :pad_width]):  # if all left padding zeros
        dem_out = dem_out[:, pad_width:]  # remove esri 0 padding left
        # pad left
        dem_out = np.pad(array=dem_out, pad_width=((0, 0), (pad_width, 0)), mode="edge")
    if not np.any(dem[:, -pad_width:]):  # if all right padding zeros
        dem_out = dem_out[:, :-pad_width]  # remove esri 0 padding right
        # pad right
        dem_out = np.pad(array=dem_out, pad_width=((0, 0), (0, pad_width)), mode="edge")
    return dem_out
