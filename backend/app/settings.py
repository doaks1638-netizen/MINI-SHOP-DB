from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from datetime import timedelta

# path to .env file — works both in Docker (/mini_shop_db/) and local dev (project root)
_here = Path(__file__).parent.parent  # backend/
parent_path = _here if (_here / ".env").exists() else _here.parent


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
    REDIRECT_URL: str

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    BASE_DIR: Path = Path(__file__).parent.parent

    YOOKASSA_SHOP_ID: int
    YOOKASSA_SECRET_KEY: str
    YOOKASSA_RETURN_URL: str


settings = Settings()  # make settings singleton
