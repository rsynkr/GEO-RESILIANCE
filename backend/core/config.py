"""
Configuration settings for Geo-Resilience Initiative
Environment variables and database configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database Settings (PostgreSQL + PostGIS) - OPTIONAL
    # The app works perfectly without a database - it's only used for storing results
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "geo_resilience"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DATABASE_URL: Optional[str] = None
    USE_DATABASE: bool = False  # Set to True only if you want to use database
    
    # Data Paths
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    INPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "inputs")
    OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "outputs")
    
    # Sentinel Hub / Planetary Computer (optional for future integration)
    SENTINEL_HUB_CLIENT_ID: Optional[str] = None
    SENTINEL_HUB_CLIENT_SECRET: Optional[str] = None
    PLANETARY_COMPUTER_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Construct DATABASE_URL only if database is enabled
        if self.USE_DATABASE and not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        
        # Create directories if they don't exist
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.INPUT_DIR, exist_ok=True)
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

# Global settings instance
settings = Settings()

