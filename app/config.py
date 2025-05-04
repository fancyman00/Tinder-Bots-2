import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

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

class RedisSettings(BaseSettings):
    HOST: str
    PORT: int
    PASS: str
    USER: str
    
    model_config = SettingsConfigDict(env_prefix="REDIS_")

class ThaifriendlySettings(BaseSettings):
    COOKIES_REDIS_DB: int
    
    model_config = SettingsConfigDict(env_prefix="THAIFRIENDLY_")

class OpenAISettings(BaseSettings):
    API_KEY: str
    ASSISTANT_ID: str
    THREADS_REDIS_DB_ID: str
    PROXY: str
    model_config = SettingsConfigDict(env_prefix="OPEN_AI_")

class OtherSettings(BaseSettings):
    
    model_config = SettingsConfigDict(env_prefix="OTHER_")



class Settings(BaseModel):
    DATABASE: DatabaseSettings = DatabaseSettings()
    REDIS: RedisSettings = RedisSettings()
    OTHER: OtherSettings = OtherSettings()
    THAIFRIENDLY: ThaifriendlySettings = ThaifriendlySettings()
    OPEN_AI: OpenAISettings = OpenAISettings()

settings = Settings()
database_url = settings.DATABASE.URL
