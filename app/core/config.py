from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    DATABASE_URL: str = "postgresql://user:passser@localhost:5432"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    APP_NAME: str = "Mon API FastAPI"
    API_V1_PREFIX: str = "/api/v1"


#@lru_cache
def get_settings():
    return Settings()


settings = get_settings()



