from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./widget_platform.db"
    JWT_SECRET: str = "change-me-in-env"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    PUBLIC_BASE_URL: str = "http://localhost:8000"
    MAX_BODY_BYTES: int = 16384
    GEO_PROVIDER_A_ENABLED: bool = True
    GEO_PROVIDER_B_ENABLED: bool = True
    MOCK_GEO_PROVIDER_A: bool = False
    MOCK_GEO_PROVIDER_B: bool = False
    NOTIFICATION_FAIL: bool = False
    PORT: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()