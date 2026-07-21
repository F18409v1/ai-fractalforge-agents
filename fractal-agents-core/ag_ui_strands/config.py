from dataclasses import dataclass


@dataclass
class FractalConfig:
    environment: str = "dev"
    log_level: str = "DEBUG"
    feature_flags: dict[str, bool] = None

    def __post_init__(self):
        if self.feature_flags is None:
            self.feature_flags = {"enable_metrics": True, "use_stub_encoder": True}
