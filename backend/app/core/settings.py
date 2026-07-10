from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path
from datetime import timedelta

# path to .env file — works both in Docker (/mini_shop_db/) and local dev (project root)
_here = Path(__file__).parent.parent  # backend/
parent_path = _here if (_here / ".env").exists() else _here.parent


class DB_Settings(BaseModel):
    USER: str
    PASS: str
    HOST: str
    PORT: int
    NAME: str
    DEBUG: bool = False

    def get_db_url(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"


class JWT_Settings(BaseModel):
    ACCESS_TOKEN_TIME: timedelta = timedelta(hours=1)
    REFRESH_TOKEN_TIME: timedelta = timedelta(days=30)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    MAX_USER_SESSION: int = 10
    CLIENT_SECRET: str
    CLIENT_ID: str
    REDIRECT_URL: str
    BASE_DIR: Path = Path(__file__).parent.parent


class YOOKASSA_Settings(BaseModel):
    SHOP_ID: int
    SECRET_KEY: str
    RETURN_URL: str


class Settings(BaseSettings):
    db: DB_Settings
    jwt: JWT_Settings
    yookassa: YOOKASSA_Settings

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


settings = Settings()  # make settings singleton
