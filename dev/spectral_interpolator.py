import numpy as np
import pystellibs
from base import PipelineStep


class SpectrumGenerator(PipelineStep):
    def __init__(self, stellib='btsettl'):
        self._stellib = stellib
        self._spec_interpolator = None
        # Set the spectral interpolator
        self.spec_grid(stellib)

    def __str__(self):
        return f'Spectrum generator with {self._stellib}'

    @property
    def stellib(self):
        return self._stellib

    @stellib.setter
    def stellib(self, new_stellib):
        self.spec_grid(new_stellib)

    def spec_grid(self, stellib=None):
        if stellib is None:
            stellib = self._stellib
        else:
            self._stellib = stellib
        if isinstance(stellib, str):
            if stellib.lower() == 'btsettl':
                self._spec_interpolator = pystellibs.BTSettl()
            if stellib.lower() == 'rauch':
                # White dwarfs
                self._spec_interpolator = pystellibs.Rauch()
            if stellib.lower() == 'elodie':
                self._spec_interpolator = pystellibs.Elodie()
            if stellib.lower() == 'basel':
                self._spec_interpolator = pystellibs.BaSeL()
            if stellib.lower() == 'koester':
                self._spec_interpolator = pystellibs.Koester()
            if stellib.lower() == 'kurucz':
                self._spec_interpolator = pystellibs.Kurucz()
            if stellib.lower() == 'marcs':
                self._spec_interpolator = pystellibs.Marcs()
            if stellib.lower() == 'phoenix':
                # TODO: Phoenix currently doesn't work due to missing data (contact the author)
                self._spec_interpolator = pystellibs.Phoenix()
            if (stellib.lower() == 'munari') or ('atlas9' in stellib.lower()):
                self._spec_interpolator = pystellibs.Munari()
        else:
            self._spec_interpolator = stellib
        return self

    def transform(self, data: dict) -> dict:
        """Generate spectra for the given parameters"""
        # Fetch the parameters
        logT = data['logT']
        logg = data['logg']
        logL = data['logL']
        Z = data['Z']
        # Compute the spectra
        points = np.array([logT, logg])
        isin_param_range = self._spec_interpolator.points_inside(points.T)
        wave, specs = self._spec_interpolator.generate_individual_spectra(
            logT=logT[isin_param_range],
            logg=logg[isin_param_range],
            logL=logL[isin_param_range],
            Z=Z[isin_param_range],
        )
        # Also already add dust extincted spectrum (just in case no extinction is applied in the pipeline)
        data.update({'wavelength': wave, 'specs': specs, 'specs_dust': specs, 'isin_param_range': isin_param_range})
        return data
