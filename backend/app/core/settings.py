from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from datetime import timedelta

# path to .env file — works both in Docker (/mini_shop_db/) and local dev (project root)
_here = Path(__file__).parent.parent  # app/
parent_path = _here if (_here / ".env").exists() else _here.parent


class Settings(BaseSettings):
    # DB
    DB__USER: str
    DB__PASS: str
    DB__HOST: str
    DB__PORT: int
    DB__NAME: str
    DEBUG: bool = False

    # JWT
    JWT__SECRET_KEY: str
    JWT__ALGORITHM: str = "HS256"
    JWT__ACCESS_TOKEN_TIME: timedelta = timedelta(hours=1)
    JWT__REFRESH_TOKEN_TIME: timedelta = timedelta(days=30)
    JWT__MAX_USER_SESSION: int = 10
    JWT__CLIENT_SECRET: str
    JWT__CLIENT_ID: str
    JWT__REDIRECT_URL: str

    # Yookassa
    YOOKASSA__SHOP_ID: int
    YOOKASSA__SECRET_KEY: str
    YOOKASSA__RETURN_URL: str

    # Computed
    BASE_DIR: Path = Path(__file__).parent.parent

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB__USER}:{self.DB__PASS}@{self.DB__HOST}:{self.DB__PORT}/{self.DB__NAME}"


settings = Settings()  # make settings singleton
