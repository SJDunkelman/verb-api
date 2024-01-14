import os
from pathlib import Path
from functools import lru_cache

# Load environment variables
if os.getenv("FASTAPI_ENV") == "development":
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')


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
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL

    WS_MESSAGE_QUEUE: str = os.environ.get("WS_MESSAGE_QUEUE", "redis://127.0.0.1:6379/0")


class DevelopmentConfig(BaseConfig):
    # Development specific configurations
    pass


class ProductionConfig(BaseConfig):
    BROKER_URL: str = os.getenv("REDIS_URL")
    RESULT_BACKEND: str = os.getenv("REDIS_URL")


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
