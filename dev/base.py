from typing import List, Tuple


class PipelineStep:
    def transform(self, data: dict) -> dict:
        raise NotImplementedError

    @staticmethod
    def check_units(phy_units: str, unit_test: dict) -> None:
        """Simple unit check"""
        for u_name, u_power in unit_test.items():
            if phy_units[u_name] != u_power:
                raise ValueError(f"Unit {u_name} not found or correct power in unit ({dict(phy_units)}).")


class PhotometryPipeline:
    def __init__(self, steps: List[Tuple[str, PipelineStep]]):
        self.steps = steps
        self.named_steps = dict(steps)  # Keep names for access

    def run(self, input_data: dict) -> dict:
        data = input_data.copy()
        for name, step in self.steps:
            data = step.transform(data)
        return data

    def __call__(self, input_data: dict) -> dict:
        return self.run(input_data)

    def get_step(self, name: str):
        """Return a step by its given name."""
        return self.named_steps[name]

    def set_params(self, **kwargs):
        """
        Set parameters of specific steps using a syntax like:
        pipeline.set_params(noise__snr=100, filter__band='g')
        """
        for key, value in kwargs.items():
            step_name, param_name = key.split("__", 1)
            step = self.get_step(step_name)
            if hasattr(step, param_name):
                setattr(step, param_name, value)
            else:
                raise AttributeError(f"{step_name} has no parameter '{param_name}'")
        return self
