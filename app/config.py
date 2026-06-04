# app/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    hf_token: str
    hf_models: str = "mistralai/Mistral-7B-Instruct-v0.3,HuggingFaceH4/zephyr-7b-beta"
    redis_url: str = "redis://localhost:6379"
    database_url: str
    rate_limit_rpm: int = 30
    daily_token_budget: int = 100_000

    @property
    def model_list(self) -> List[str]:
        return [m.strip() for m in self.hf_models.split(",")]

    class Config: 
        env_file = ".env"

settings = Settings()