"""Configuration management for Futu MCP Server."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class FutuConfig(BaseSettings):
    """Futu API configuration settings."""

    # FutuOpenD connection settings
    host: str = Field(default="127.0.0.1", description="FutuOpenD host address")
    port: int = Field(default=11111, description="FutuOpenD port number")
    
    # Trading password (required for trading operations)
    trade_pwd: Optional[str] = Field(default=None, description="Trading password for unlocking trade")
    
    # Connection settings
    connection_timeout: int = Field(default=30, description="Connection timeout in seconds")
    request_timeout: int = Field(default=60, description="Request timeout in seconds")
    
    # Market data settings
    max_subscription_quota: int = Field(default=500, description="Maximum subscription quota")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "FUTU_"
        env_file = ".env"
        case_sensitive = False


def get_config() -> FutuConfig:
    """Get Futu configuration from environment variables."""
    return FutuConfig()

