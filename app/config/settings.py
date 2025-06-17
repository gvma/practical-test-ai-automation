from functools import lru_cache
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    SCHEDULER_SECONDS_INTERVAL: int
    SLACK_WEBHOOK_URL: str
    SLA_CONFIG_PATH: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Config:
    return Config() # type: ignore

settings = get_settings()