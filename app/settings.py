from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from datetime import timedelta

parent_path = Path(__file__).parent.parent  # path to .env file in project path


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    debug: bool = False

    def get_db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    ACCESS_TOKEN_TIME: timedelta = timedelta(hours=1)
    REFRESH_TOKEN_TIME: timedelta = timedelta(days=30)

    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"

    MAX_USER_SESSION: int = 10

    CLIENT_SECRET: str
    CLIENT_ID: str
    REDIRECT_URL: str = "http://localhost:8000/api/v1/auth/google/callback"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    BASE_DIR: Path = Path(__file__).parent.parent


settings = Settings()  # make settings singleton
