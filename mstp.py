"""
NAME:
    RVT Anisotropic Multi-scale topographic position esri raster function
    rvt_py, rvt.vis.mstp

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
import gc


class RVTMstp:
    def __init__(self):
        self.name = "RVT Multi-scale topographic position"
        self.description = "Calculates Multi-scale topographic position."
        # default values
        self.local_scale_min = 1.
        self.local_scale_max = 5.
        self.local_scale_step = 1.
        self.meso_scale_min = 5.
        self.meso_scale_max = 50.
        self.meso_scale_step = 5.
        self.broad_scale_min = 50.
        self.broad_scale_max = 500.
        self.broad_scale_step = 50.
        self.lightness = 1.2
        self.padding = int(self.broad_scale_max)

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "Input raster for which to create the MSTP."
            },
            {
                'name': 'local_scale_min',
                'dataType': 'numeric',
                'value': self.local_scale_min,
                'required': True,
                'displayName': "Local scale minimum",
                'description': "Local scale minimum radius."
            },
            {
                'name': 'local_scale_max',
                'dataType': 'numeric',
                'value': self.local_scale_max,
                'required': True,
                'displayName': "Local scale maximum",
                'description': "Local scale maximum radius."
            },
            {
                'name': 'local_scale_step',
                'dataType': 'numeric',
                'value': self.local_scale_step,
                'required': True,
                'displayName': "Local scale step",
                'description': "Local scale step radius."
            },
            {
                'name': 'meso_scale_min',
                'dataType': 'numeric',
                'value': self.meso_scale_min,
                'required': True,
                'displayName': "Meso scale minimum",
                'description': "Meso scale minimum radius."
            },
            {
                'name': 'meso_scale_max',
                'dataType': 'numeric',
                'value': self.meso_scale_max,
                'required': True,
                'displayName': "Meso scale maximum",
                'description': "Meso scale maximum radius."
            },
            {
                'name': 'meso_scale_step',
                'dataType': 'numeric',
                'value': self.meso_scale_step,
                'required': True,
                'displayName': "Meso scale step",
                'description': "Meso scale step radius."
            },
            {
                'name': 'broad_scale_min',
                'dataType': 'numeric',
                'value': self.broad_scale_min,
                'required': True,
                'displayName': "Broad scale minimum",
                'description': "Broad scale minimum radius."
            },
            {
                'name': 'broad_scale_max',
                'dataType': 'numeric',
                'value': self.broad_scale_max,
                'required': True,
                'displayName': "Broad scale maximum",
                'description': "Broad scale maximum radius."
            },
            {
                'name': 'broad_scale_step',
                'dataType': 'numeric',
                'value': self.broad_scale_step,
                'required': True,
                'displayName': "Broad scale step",
                'description': "Broad scale step radius."
            },
            {
                'name': 'lightness',
                'dataType': 'numeric',
                'value': self.lightness,
                'required': True,
                'displayName': "Lightness",
                'description': "Lightness to control MSTP brightness."
            }
        ]

    def getConfiguration(self, **scalars):
        self.prepare(local_scale_min=scalars.get('local_scale_min'), local_scale_max=scalars.get('local_scale_max'),
                     local_scale_step=scalars.get('local_scale_step'), meso_scale_min=scalars.get('meso_scale_min'),
                     meso_scale_max=scalars.get('meso_scale_max'), meso_scale_step=scalars.get('meso_scale_step'),
                     broad_scale_min=scalars.get('broad_scale_min'), broad_scale_max=scalars.get('broad_scale_max'),
                     broad_scale_step=scalars.get('broad_scale_step'), lightness=scalars.get('lightness')
                     )
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
        kwargs['output_info']['bandCount'] = 3
        r = kwargs['raster_info']
        kwargs['output_info']['noData'] = np.nan
        kwargs['output_info']['pixelType'] = 'u1'
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['statistics'] = ()
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        dem = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)[0]  # Input pixel array.
        dem = change_0_pad_to_edge_pad(dem, self.padding)
        no_data = props["noData"]
        if no_data is not None:
            no_data = props["noData"][0]

        mstp = rvt.vis.mstp(dem=dem, local_scale=(self.local_scale_min, self.local_scale_max, self.local_scale_step),
                            meso_scale=(self.meso_scale_min, self.meso_scale_max, self.meso_scale_step),
                            broad_scale=(self.broad_scale_min, self.broad_scale_max, self.broad_scale_step),
                            lightness=self.lightness, no_data=no_data)
        mstp = mstp[:, self.padding:-self.padding, self.padding:-self.padding]  # remove padding

        pixelBlocks['output_pixels'] = mstp.astype(props['pixelType'], copy=False)

        # release memory
        del dem
        del no_data
        del mstp
        gc.collect()

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            name = "MSTP_L{}.tif".format(self.lightness)
            keyMetadata['datatype'] = 'Processed'
            keyMetadata['productname'] = 'RVT {}'.format(name)
        return keyMetadata

    def prepare(self, local_scale_min=1, local_scale_max=10, local_scale_step=1, meso_scale_min=10, meso_scale_max=50,
                meso_scale_step=5, broad_scale_min=50, broad_scale_max=500, broad_scale_step=50, lightness=1.2):
        self.local_scale_min = int(local_scale_min)
        self.local_scale_max = int(local_scale_max)
        self.local_scale_step = int(local_scale_step)
        self.meso_scale_min = int(meso_scale_min)
        self.meso_scale_max = int(meso_scale_max)
        self.meso_scale_step = int(meso_scale_step)
        self.broad_scale_min = int(broad_scale_min)
        self.broad_scale_max = int(broad_scale_max)
        self.broad_scale_step = int(broad_scale_step)
        self.lightness = float(lightness)
        self.padding = int(self.broad_scale_max)


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