class ProdConfig:
    ENV = "production"
    DEBUG = False
    LOG_LEVEL = "INFO"
    DATABASE_URL = "postgresql://user:pass@localhost/pro_experience"
    FEATURE_FLAGS = {
        "use_stub_models": False,
        "enable_experience_logging": True,
    }
