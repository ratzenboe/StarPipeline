import extinction
import numpy as np
from base import PipelineStep


class DustAttenuator(PipelineStep):
    def __init__(self, law='fitzpatrick'):
        self._law = law.lower()
        self._av_law = None
        self.av_law()

    def __str__(self):
        return f'Application of extinction law: {self._law}'

    @property
    def law(self):
        return self._law

    @law.setter
    def law(self, new_law):
        self.av_law(new_law)

    def av_law(self, law=None):
        """ Set the extinction law to be used"""
        if law is None:
            law = self._law
        else:
            self._law = law
        if isinstance(law, str):
            law_choices = [
                'cardelli',
                'odonnell',
                'calzetti',
                'fitzpatrick'
            ]
            if law not in law_choices:
                err_msg = f'Input {law} not available.'
                err_msg += 'Extinction  laws are: `cardelli`, `odonnell`, `calzetti`, and `fitzpatrick`'
                raise ValueError(err_msg)
            # extinction laws
            law_f = None
            if self._law == law_choices[0]:
                law_f = extinction.ccm89
            if self._law == law_choices[1]:
                law_f = extinction.odonnell94
            if self._law == law_choices[2]:
                law_f = extinction.calzetti00
            if self._law == law_choices[3]:
                law_f = extinction.fitzpatrick99
            self._av_law = law_f
        else:
            self._av_law = law
        # Vectorized version allows for Av and Rv to be arrays
        self._av_law = np.vectorize(self._av_law, signature='(n),(),(),()->(n)')
        return self

    def apply_extinction(self, wave, specs, Av, Rv):
        # test units
        self.check_units(wave.units, {'angstrom': 1.0})
        self.check_units(specs.units, {'erg': 1.0, 'second': -1.0, 'angstrom': -1.0})
        # Compute extinction
        dust_specs = specs.copy()
        # Compute extinction
        Dlambda = np.exp(-1 * self._av_law(wave.magnitude, Av, Rv, unit='aa'))
        if len(Dlambda[None, :].shape) == 1:
            # In case Av and Rv are scalars
            Dlambda = Dlambda[:, None]
        # save extingted spectra, keep units
        dust_specs._magnitude *= Dlambda
        return dust_specs

    def transform(self, data: dict) -> dict:
        """Apply dust extinction to the spectra"""
        # Fetch the parameters
        wave = data['wavelength']
        specs = data['specs']
        Av = data.get('Av', 0)
        Rv = data.get('Rv', 3.1)
        # Apply extinction
        dust_specs = self.apply_extinction(wave, specs, Av, Rv)
        # Update dust specs in data
        data['specs_dust'] = dust_specs
        return data
