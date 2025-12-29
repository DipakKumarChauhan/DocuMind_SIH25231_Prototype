from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    ENV: str = os.getenv("ENV", "development")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()