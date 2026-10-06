import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Canteen Orchestration System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "smart_canteen_super_secure_jwt_secret_key_2026_campus_auth")
    QR_SECRET_KEY: str = os.getenv("QR_SECRET_KEY", "smart_canteen_hmac_qr_signature_key_for_pickup_tokens_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./smart_canteen.db")
    SYNC_DATABASE_URL: str = os.getenv("SYNC_DATABASE_URL", "sqlite:///./smart_canteen.db")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # Operational & Dynamic ETA Weights
    DEFAULT_KITCHEN_ACTIVE_STATIONS: int = 4
    KITCHEN_THROUGHPUT_PER_STATION_PER_MIN: float = 0.35  # avg items prepped per min
    BASE_TRANSITION_BUFFER_MINUTES: int = 2
    
    # Queue Fair Aging Parameters
    WEIGHT_WAITING_TIME: float = 0.50
    WEIGHT_DEADLINE_URGENCY: float = 0.30
    WEIGHT_PREP_COMPLEXITY: float = 0.20
    AGING_BONUS_PER_MINUTE: float = 1.25  # increases priority over time to prevent starvation
    
    # Peak Load Thresholds
    PEAK_BUSY_ACTIVE_ORDERS: int = 15
    PEAK_HIGH_ACTIVE_ORDERS: int = 30
    PEAK_CRITICAL_ACTIVE_ORDERS: int = 45
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
