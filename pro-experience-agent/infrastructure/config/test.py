class TestConfig:
    ENV = "test"
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_URL = "sqlite:///./test.db"
    FEATURE_FLAGS = {
        "use_stub_models": True,
        "enable_experience_logging": False,
    }
