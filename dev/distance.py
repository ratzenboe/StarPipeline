import numpy as np
from pyphot import unit
from base import PipelineStep


class Distance(PipelineStep):
    def __init__(self):
        pass

    def transform(self, data: dict) -> dict:
        """Calculate distance from absolute magnitude"""
        # Fetch the parameters
        distance_pc = data['distance']
        specs = data['specs']
        dust_specs = data['specs_dust']
        isin_param_range = data['isin_param_range']
        # Check units
        self.check_units(specs.units, {'erg': 1.0, 'second': -1.0, 'angstrom': -1.0})
        self.check_units(dust_specs.units, {'erg': 1.0, 'second': -1.0, 'angstrom': -1.0})
        # Comvert distance from pc to cm
        # -> also make sure to only use distances to stars we have spectra for
        distance = distance_pc[isin_param_range] * unit['pc']
        distance_cm = distance.to(unit['cm'])
        flux_at_earth = specs.magnitude / (4 * np.pi * distance_cm.magnitude[..., None] ** 2)
        flux_dust_at_earth = dust_specs.magnitude / (4 * np.pi * distance_cm.magnitude[..., None] ** 2)
        # Add units
        flux_at_earth *= unit['erg'] / (unit['cm'] ** 2 * unit['Angstrom'] * unit['s'])
        flux_dust_at_earth *= unit['erg'] / (unit['cm'] ** 2 * unit['Angstrom'] * unit['s'])
        # Add the distance to the data dictionary
        data.update({'flam': flux_at_earth, 'flam_dust': flux_dust_at_earth})
        return data