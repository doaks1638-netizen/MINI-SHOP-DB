from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

parent_path = Path(__file__).parent.parent  # path to .env file in project path


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    def get_db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(extra="ignore", env_file=parent_path / ".env")


settings = Settings()  # make settings singlitone
