"""
Relief Visualization Toolbox – Visualization Functions

RVT Sky illumination raster function
rvt_py, rvt.vis.sky_illumination

Credits:
    Žiga Kokalj (ziga.kokalj@zrc-sazu.si)
    Krištof Oštir (kristof.ostir@fgg.uni-lj.si)
    Klemen Zakšek
    Klemen Čotar
    Maja Somrak
    Žiga Maroh

Copyright:
    2010-2020 Research Centre of the Slovenian Academy of Sciences and Arts
    2016-2020 University of Ljubljana, Faculty of Civil and Geodetic Engineering
"""

import numpy as np
import rvt.vis


class RVTSkyIllum:
    def __init__(self):
        self.name = "RVT Sky illumination"
        self.description = "Calculates Sky illumination."
        # default values
        self.sky_model = "overcast"
        self.compute_shadow = True
        self.max_fine_radius = 100.
        self.num_directions = 32.
        self.shadow_az = 315.
        self.shadow_el = 35.
        self.padding = 10

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "Input raster for which to create the Sky illumination map."
            },
            {
                'name': 'sky_model',
                'dataType': 'string',
                'value': self.sky_model,
                'required': True,
                'displayName': 'Sky model',
                'domain': ('uniform', 'overcast'),
                'description': "Sky model, it can be 'overcast' or 'uniform'."
            },
            {
                'name': 'compute_shadow',
                'dataType': 'boolean',
                'value': self.compute_shadow,
                'required': True,
                'displayName': "Compute shadow",
                'description': "If True it computes shadow."
            },
            {
                'name': 'max_fine_radius',
                'dataType': 'numeric',
                'value': self.max_fine_radius,
                'required': True,
                'displayName': "Max shadow modeling",
                'description': "Max shadow modeling distance [pixels]."
            },
            {
                'name': 'num_directions',
                'dataType': 'numeric',
                'value': self.num_directions,
                'required': True,
                'displayName': "Number of directions",
                'description': "Number of directions to search for horizon."
            },
            {
                'name': 'shadow_az',
                'dataType': 'numeric',
                'value': self.shadow_az,
                'required': True,
                'displayName': "Shadow azimuth",
                'description': "Shadow azimuth."
            },
            {
                'name': 'shadow_el',
                'dataType': 'numeric',
                'value': self.shadow_el,
                'required': True,
                'displayName': "Shadow elevation",
                'description': "Shadow elevation."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(sky_model=scalars.get('sky_model'), compute_shadow=scalars.get("compute_shadow"),
                     max_fine_radius=scalars.get("max_fine_radius"), num_directions=scalars.get("num_directions"),
                     shadow_az=scalars.get("shadow_az"), shadow_el=scalars.get("shadow_el"))
        return {
            'compositeRasters': False,
            'inheritProperties': 2 | 4,
            'invalidateProperties': 2 | 4 | 8,
            'inputMask': False,
            'resampling': False,
            'padding': self.padding,
            'resamplingType': 4
        }

    def updateRasterInfo(self, **kwargs):
        kwargs['output_info']['bandCount'] = 1
        r = kwargs['raster_info']
        kwargs['output_info']['noData'] = -3.4028235e+038
        kwargs['output_info']['pixelType'] = 'f4'
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['statistics'] = ()
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        dem = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)[0]  # Input pixel array.
        dem = change_0_pad_to_edge_pad(dem=dem, pad_width=self.padding)
        pixel_size = props['cellSize']

        if (pixel_size[0] <= 0) | (pixel_size[1] <= 0):
            raise Exception("Input raster cell size is invalid.")

        sky_illum = rvt.vis.sky_illumination(dem=dem, resolution=pixel_size[0], sky_model=self.sky_model,
                                             compute_shadow=self.compute_shadow, max_fine_radius=self.max_fine_radius,
                                             num_directions=self.num_directions, shadow_az=self.shadow_az,
                                             shadow_el=self.shadow_el)
        sky_illum = sky_illum[self.padding:-self.padding, self.padding:-self.padding]  # remove padding

        pixelBlocks['output_pixels'] = sky_illum.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def prepare(self, sky_model="overcast", compute_shadow=True, max_fine_radius=100, num_directions=32, shadow_az=315,
                shadow_el=35):
        self.sky_model = str(sky_model)
        self.compute_shadow = bool(compute_shadow)
        self.max_fine_radius = int(max_fine_radius)
        self.num_directions = int(num_directions)
        self.shadow_az = int(shadow_az)
        self.shadow_el = int(shadow_el)
        self.padding = 10


def change_0_pad_to_edge_pad(dem, pad_width):
    dem = dem[pad_width:-pad_width, pad_width:-pad_width]  # remove esri 0 padding
    dem = np.pad(array=dem, pad_width=pad_width, mode="edge")  # add new edge padding
    return dem
