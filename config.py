import os
from typing import Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # postgres
    open_ai_api_key: Optional[str] = None
    upload_dir: Optional[str] = 'uploads'
    config_path: Optional[str] = 'config.toml'
    vanna_model_name: Optional[str]
    vanna_api_key: Optional[str]

    
    class Config:
        env_file = f'.env'
        extra = "ignore"

settings = Settings()