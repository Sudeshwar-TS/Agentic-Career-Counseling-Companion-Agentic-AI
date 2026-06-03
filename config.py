from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = "9a7f6d4c2e0b8a1f5d3c7b9e6a4f2d0c8b1a5e9d3c6f7a2b4e8c1d5f9a0b3c6"
    algorithm: str = "HS256"
    token_minutes: int = 1440
    database_url: str = "sqlite:///./careernav.db"
    cors_origin: str = "http://localhost:5173"
    chroma_path: str = "./chroma_db"
    watsonx_api_key: str = ""
    watsonx_project_id: str = ""
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    granite_model_id: str = "ibm/granite-13b-instruct-v2"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def settings() -> Settings:
    return Settings()
