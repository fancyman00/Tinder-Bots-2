import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class DatabaseSettings(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    DB: str
    PORT: str
    ENGINE: str
    
    @property
    def URL(self) -> str:
        return f"{self.ENGINE}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_")
    
class Settings(BaseSettings):
    DATABASE: DatabaseSettings = DatabaseSettings()
    SECRET_KEY: str
    ALGORITHM: str


# Получаем параметры для загрузки переменных среды
settings = Settings()
database_url = settings.DATABASE.URL
