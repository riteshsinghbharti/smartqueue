import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Virtual Queue - Clinic Edition"
    API_V1_STR: str = "/api"
    
    # SQLite database path (in-container or mounted volume)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./clinic_queue.db")
    
    # CORS Origins (Comma-separated)
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,*"
    )
    
    # Frontend Base URL (encoded into QR code)
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    
    # In-memory cache TTL in seconds
    CACHE_TTL_SECONDS: int = 30

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
