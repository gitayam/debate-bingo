from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator, Field
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "Debate Bingo API"
    API_V1_STR: str = "/api/v1"
    
    # Database - SQLite for local development, PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./debate_bingo_dev.db"
    TEST_DATABASE_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security - CRITICAL: Must be set in environment variables
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        min_length=32,
        description="JWT Secret Key - MUST be set in production via environment variable"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS - Restrict in production
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3745",
        "http://localhost:3746", 
        "http://127.0.0.1:3745",
        "http://127.0.0.1:3746"
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Security Headers
    ENABLE_SECURITY_HEADERS: bool = True
    ENABLE_HTTPS_REDIRECT: bool = False  # Enable in production
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Deprecated fields for backward compatibility
    ALGORITHM: Optional[str] = None  # Use JWT_ALGORITHM instead
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()