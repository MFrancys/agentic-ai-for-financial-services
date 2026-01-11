"""
Configuration management for Financial AI Advisor.

This module centralizes all configuration settings, making the application
easier to maintain and deploy across different environments.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for LLM models."""
    name: str
    provider: ModelProvider
    max_tokens: int
    temperature: float
    cost_per_1k_input: float
    cost_per_1k_output: float


class Config:
    """
    Application configuration.
    
    Centralizes all settings and provides type-safe access to configuration values.
    Uses environment variables with sensible defaults.
    """
    
    # Environment
    ENVIRONMENT: Environment = Environment(
        os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value)
    )
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Model Configuration
    DEFAULT_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    DEFAULT_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    # Model Pricing (per 1K tokens)
    MODELS = {
        "gpt-4o-mini": ModelConfig(
            name="gpt-4o-mini",
            provider=ModelProvider.OPENAI,
            max_tokens=16384,
            temperature=0.7,
            cost_per_1k_input=0.00015,
            cost_per_1k_output=0.0006,
        ),
        "gpt-4o": ModelConfig(
            name="gpt-4o",
            provider=ModelProvider.OPENAI,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_input=0.005,
            cost_per_1k_output=0.015,
        ),
        "gpt-4": ModelConfig(
            name="gpt-4",
            provider=ModelProvider.OPENAI,
            max_tokens=8192,
            temperature=0.7,
            cost_per_1k_input=0.03,
            cost_per_1k_output=0.06,
        ),
        "claude-3-sonnet-20240229": ModelConfig(
            name="claude-3-sonnet-20240229",
            provider=ModelProvider.ANTHROPIC,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_input=0.003,
            cost_per_1k_output=0.015,
        ),
    }
    
    # Retry Configuration
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "1.0"))
    RETRY_BACKOFF: float = float(os.getenv("RETRY_BACKOFF", "2.0"))
    
    # Streamlit Configuration
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    STREAMLIT_THEME: str = os.getenv("STREAMLIT_THEME", "dark")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Feature Flags
    ENABLE_AB_TESTING: bool = os.getenv("ENABLE_AB_TESTING", "True").lower() == "true"
    ENABLE_VISUALIZATIONS: bool = os.getenv("ENABLE_VISUALIZATIONS", "True").lower() == "true"
    ENABLE_HISTORY: bool = os.getenv("ENABLE_HISTORY", "True").lower() == "true"
    
    # Validation
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "True").lower() == "true"
    
    @classmethod
    def get_model_config(cls, model_name: str) -> ModelConfig:
        """
        Get configuration for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelConfig object
            
        Raises:
            ValueError: If model is not supported
        """
        config = cls.MODELS.get(model_name)
        if not config:
            raise ValueError(
                f"Unsupported model: {model_name}. "
                f"Supported models: {list(cls.MODELS.keys())}"
            )
        return config
    
    @classmethod
    def estimate_cost(
        cls, 
        model_name: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """
        Estimate cost for a model request.
        
        Args:
            model_name: Name of the model
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        config = cls.get_model_config(model_name)
        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output
        return input_cost + output_cost
    
    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if cls.REQUIRE_API_KEY:
            if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
                errors.append("At least one API key must be set (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        
        if cls.DEFAULT_MODEL not in cls.MODELS:
            errors.append(f"Invalid DEFAULT_MODEL: {cls.DEFAULT_MODEL}")
        
        if not 0 <= cls.DEFAULT_TEMPERATURE <= 2:
            errors.append(f"DEFAULT_TEMPERATURE must be between 0 and 2, got {cls.DEFAULT_TEMPERATURE}")
        
        if cls.DEFAULT_MAX_TOKENS <= 0:
            errors.append(f"DEFAULT_MAX_TOKENS must be positive, got {cls.DEFAULT_MAX_TOKENS}")
        
        return errors


# Validate configuration on import
_validation_errors = Config.validate()
if _validation_errors and Config.ENVIRONMENT == Environment.PRODUCTION:
    raise ValueError(f"Configuration validation failed: {', '.join(_validation_errors)}")
elif _validation_errors and Config.DEBUG:
    print(f"⚠️  Configuration warnings: {', '.join(_validation_errors)}")

