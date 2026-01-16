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
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN")
    HF_EMBEDDING_MODEL: str = os.getenv("HF_EMBEDDING_MODEL")
    HF_API_URL_BGE: str = os.getenv("HF_API_URL_BGE")
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    # Local path to a pre-downloaded CLIP model folder (optional)
    CLIP_MODEL_PATH: str | None = os.getenv("CLIP_MODEL_PATH")
    # Central model cache directory (where all models are stored and reused)
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "/home/dipak/SIH-25321_MVP/model_cache")
    ASR_MODE = "auto" # Options: auto | remote | local
    
    ASR_REMOTE_API_URL: str = os.getenv("ASR_REMOTE_API_URL")
    ASR_REMOTE_API_KEY: str = os.getenv("ASR_REMOTE_API_KEY")

    IMAGE_EMBEDDING_MODE: str = "auto"
    IMAGE_EMBEDDING_API_URL: str = os.getenv("IMAGE_EMBEDDING_API_URL")
    IMAGE_EMBEDDING_API_KEY: str = os.getenv("IMAGE_EMBEDDING_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()   

# Ensure cache directory exists and configure libraries to use it
try:
    os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
except Exception:
    # If directory creation fails, continue; individual loaders may handle their own paths
    pass

# Configure Hugging Face caches to use the central cache directory
os.environ.setdefault("TRANSFORMERS_CACHE", settings.MODEL_CACHE_DIR)
os.environ.setdefault("HF_HOME", settings.MODEL_CACHE_DIR)
os.environ.setdefault("HF_HUB_CACHE", settings.MODEL_CACHE_DIR)

# Some libraries respect XDG cache; set it as well
os.environ.setdefault("XDG_CACHE_HOME", settings.MODEL_CACHE_DIR)