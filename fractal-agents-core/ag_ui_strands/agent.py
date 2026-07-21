from .config import FractalConfig


class FractalAgent:
    """Core experience agent abstraction for the fractal agents crate."""

    def __init__(self, config: FractalConfig):
        self.config = config

    def handle(self, payload: dict) -> dict:
        return {"status": "ok", "payload": payload, "env": self.config.environment}
