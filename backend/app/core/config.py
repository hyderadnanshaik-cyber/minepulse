import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "MINEGUARD — Mine Subsidence Monitoring Backend"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"

    # Primary database — PostgreSQL 18 + PostGIS
    DATABASE_URL: str = "postgresql+asyncpg://postgres:adnan2007?@localhost:5432/mine_monitoring"
    SYNC_DATABASE_URL: Optional[str] = "postgresql+psycopg2://postgres:adnan2007?@localhost:5432/mine_monitoring"

    # MQTT
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_KEEPALIVE: int = 60

    # Firebase — path to serviceAccountKey.json or leave blank for dev mock-auth
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:8000"

    # Gateway
    GATEWAY_ID: str = "MINEGATE-01"
    GATEWAY_LOCAL_URL: str = "http://localhost:8000"
    GATEWAY_API_KEY: Optional[str] = None
    ALARM_GPIO_PIN: int = 18

    # Email & SMS (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    SMTP_FROM: str = "noreply@mineguard.local"
    SMS_PROVIDER: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    SMS_FROM: Optional[str] = None

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
