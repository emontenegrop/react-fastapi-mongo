import os
from typing import List, Optional
from urllib.parse import quote_plus
from pydantic import Field, field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors_origins(v) -> List[str]:
    """Parse CORS origins from string or list"""
    if isinstance(v, str):
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    return v


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Database Configuration
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = Field(default=27017, ge=1, le=65535)
    MONGO_DB: str
    
    # Security Configuration
    SECRET_KEY: Optional[str] = Field(default=None)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=10080)
    CORS_ORIGINS: str = Field(default="http://localhost:3000")
    
    # Performance Configuration
    MAX_FILE_SIZE: int = Field(default=10485760, ge=1024)  # 10MB minimum 1KB
    CONNECTION_POOL_SIZE: int = Field(default=10, ge=1, le=100)
    REQUEST_TIMEOUT: int = Field(default=30, ge=1, le=300)
    
    # Application Configuration
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    SERVER_PATH: str = Field(default="/code/repo")
    TIMEOUT: int = Field(default=10, ge=1, le=300)
    
    # External Services
    WS_VALIDACION_FIRMA: AnyHttpUrl
    BACK_LOGS: AnyHttpUrl
    
    # Caching Configuration
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = Field(default=0, ge=0, le=15)
    CACHE_TTL: int = Field(default=3600, ge=1)  # 1 hour default
    CACHE_DEFAULT_TTL: int = Field(default=3600, ge=1)  # Default cache TTL
    REDIS_MAX_CONNECTIONS: int = Field(default=10, ge=1, le=100)
    
    # Monitoring Configuration
    ENABLE_METRICS: bool = Field(default=True)
    METRICS_PORT: int = Field(default=8090, ge=1024, le=65535)
    SENTRY_DSN: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1)
    RATE_LIMIT_WINDOW: int = Field(default=60, ge=1)  # seconds
    
    @field_validator('SECRET_KEY', mode='before')
    @classmethod
    def validate_secret_key(cls, v):
        if v is None:
            # Try to read from secrets file first (Docker secrets)
            secret_file = "/run/secrets/jwt_secret"
            if os.path.exists(secret_file):
                with open(secret_file, 'r') as f:
                    return f.read().strip()
            # Fallback to environment variable
            secret = os.getenv("SECRET_KEY")
            if not secret:
                raise ValueError("SECRET_KEY is required")
            return secret
        return v
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        return v.upper()
    
    @property
    def mongo_url(self) -> str:
        """Construct MongoDB connection URL with properly escaped credentials"""
        escaped_user = quote_plus(self.MONGO_USER)
        escaped_password = quote_plus(self.MONGO_PASSWORD)
        return f"mongodb://{escaped_user}:{escaped_password}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}?authSource=admin"
    
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL with properly escaped credentials"""
        if self.REDIS_PASSWORD:
            escaped_password = quote_plus(self.REDIS_PASSWORD)
            auth = f":{escaped_password}@"
        else:
            auth = ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string to list"""
        return parse_cors_origins(self.CORS_ORIGINS)


settings = Settings()
