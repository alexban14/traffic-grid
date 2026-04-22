from typing import List
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TrafficGrid"

    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "trafficgrid"
    DATABASE_URL: str = ""

    REDIS_URL: str = "redis://redis:6379/0"

    # JWT / Auth
    JWT_SECRET_KEY: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    ADMIN_PASSWORD: str = "admin"

    @model_validator(mode="after")
    def assemble_db_url(self):
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    model_config = {"case_sensitive": True}


settings = Settings()
