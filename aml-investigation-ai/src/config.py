"""Configuration management for AML Investigation AI system."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(default=None, env="OPENAI_BASE_URL")
    model_name: str = Field(default="gpt-4o-mini", env="MODEL_NAME")
    temperature: float = Field(default=0.3, env="TEMPERATURE")
    max_tokens: int = Field(default=800, env="MAX_TOKENS")
    
    # Investigation Settings
    max_iterations: int = Field(default=5, env="MAX_ITERATIONS")
    enable_mock_data: bool = Field(default=True, env="ENABLE_MOCK_DATA")
    
    # Regulatory Thresholds
    ctr_threshold: float = Field(default=10000.0, env="CTR_THRESHOLD")
    sar_risk_threshold: float = Field(default=7.0, env="SAR_RISK_THRESHOLD")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database (for future production use)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def validate_configuration() -> bool:
    """Validate required configuration is present."""
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required")
    
    if settings.temperature < 0 or settings.temperature > 2:
        raise ValueError("TEMPERATURE must be between 0 and 2")
    
    if settings.max_iterations < 1:
        raise ValueError("MAX_ITERATIONS must be at least 1")
    
    return True

