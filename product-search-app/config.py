"""
Configuration management for the Product Search API
Loads settings from environment variables with defaults
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Elasticsearch Configuration
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "amazon_products"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Search Configuration
    default_search_size: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance
    Uses lru_cache to ensure settings are loaded only once
    """
    return Settings()
