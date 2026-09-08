from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OIL Safety Intelligence"
    API_V1_STR: str = "/api/v1"
    
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "sif_db"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/sif_db"
    
    GEMINI_API_KEY: str = ""
    API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # Phase 2 configurations
    AI_PROVIDER: str = "gemini"          # gemini | mock | local
    AI_TIMEOUT_SECONDS: int = 10
    AI_MAX_RETRIES: int = 3
    LANGUAGE_CONFIDENCE_THRESHOLD: float = 0.90
    MIN_REPORT_LENGTH: int = 10
    MIN_SAMPLE_SIZE: int = 30
    APP_MODE: str = "hybrid"             # offline | hybrid
    PIPELINE_VERSION: str = "1.0.0"
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
