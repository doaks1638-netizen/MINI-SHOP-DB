from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from datetime import timedelta

# path to .env file — works both in Docker (/mini_shop_db/) and local dev (project root)
_here = Path(__file__).parent.parent  # app/
parent_path = _here if (_here / ".env").exists() else _here.parent



class Settings(BaseSettings):
    # DB
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DEBUG: bool = False

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_TIME: timedelta = timedelta(hours=1)
    JWT_REFRESH_TOKEN_TIME: timedelta = timedelta(days=30)
    JWT_MAX_USER_SESSION: int = 10
    JWT_CLIENT_SECRET: str
    JWT_CLIENT_ID: str
    JWT_REDIRECT_URL: str

    # Yookassa
    YOOKASSA_SHOP_ID: int
    YOOKASSA_SECRET_KEY: str
    YOOKASSA_RETURN_URL: str

    # Computed
    BASE_DIR: Path = Path(__file__).parent.parent.parent

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
    )

    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()  # make settings singleton
