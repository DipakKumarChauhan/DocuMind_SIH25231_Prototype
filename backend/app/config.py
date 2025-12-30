from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    ENV: str = os.getenv("ENV", "development")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_DAYS", "7"))
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()