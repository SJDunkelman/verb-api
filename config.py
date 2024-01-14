import os
from pathlib import Path
from functools import lru_cache


class BaseConfig:
    # Paths
    ROOT_DIR = Path(__file__).parent.absolute()

    # API
    API_NAME = "Verb"
    DESCRIPTION = ""

    # Database
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
    SUPABASE_ANON_KEY: str = os.environ.get("SUPABASE_ANON_KEY")

    # Storage buckets

    # Celery task queue
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")


class DevelopmentConfig(BaseConfig):
    # Development specific configurations
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    # Testing specific configurations
    pass


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_name = os.environ.get("FASTAPI_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
