from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Relay"
    DATABASE_URL: str = "postgresql://relay:relay_password@postgres:5432/relay"
    REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()