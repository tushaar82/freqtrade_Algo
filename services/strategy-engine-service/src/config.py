"""
Configuration Management
VELOX Strategy Engine Service
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Service configuration from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://velox:velox123@localhost:5432/velox_trading"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Strategy
    STRATEGY_DIR: str = "./src/strategies"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
