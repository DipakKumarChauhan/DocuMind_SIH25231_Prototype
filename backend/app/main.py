
##################### Imports #####################

from fastapi import FastAPI
from app.config import settings
from app.middleware.cors import setup_cors
from app.db.qdrant_collections import create_collections
from app.db.qdrant_client import get_qdrant_client
from app.llm.groq_client import generate_completion, LLMServiceError

################## Importing API routers ##################
from app.api.upload_admin import route as upload_admin_router
from app.api.search import router as search_router
from app.api.admin_tfidf import router as admin_tfidf_router
from app.api.upload_image import router as upload_image_router
from app.api.search_image import router as search_image_router
from app.api.upload_audio import router as upload_audio_router
from app.api.search_audio import router as search_audio_router

########################################################
from app.db.session import engine
from app.db.base import Base
from app.auth.models import User
from app.auth.routes import router as auth_router


#from app.db.qdrant_setup import setup_qdrant_collections ## New Change


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Multimodal RAG Back-end",
    version="0.1.0",
)

#injecing Cors Middleware
setup_cors(app)

# Registering API routers 
app.include_router(upload_admin_router)
app.include_router(auth_router)
app.include_router(search_router)
app.include_router(admin_tfidf_router)
app.include_router(upload_image_router)
app.include_router(search_image_router)
app.include_router(upload_audio_router)
app.include_router(search_audio_router)
# app.include_router(search_image_router)

#################### Startup Event ####################

@app.on_event("startup")
def startup_event():
    client = get_qdrant_client()
    client.get_collections()

    create_collections()


#################### API ROUTES ####################

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Multimodal RAG Back-end!"}


@app.get("/health", tags=["Health"])
def health_cehck():
    return{
        "message":"API is healthy",
        "status": "ok",
        "env": settings.ENV
    }

@app.get("/health/qdrant", tags=["Health"])
def qdrant_health():
    client = get_qdrant_client()
    collections = client.get_collections()
    return{
        "status":"ok",
        "collections": [c.name for c in collections.collections]
    }

@app.get("/health/llm", tags=["Health"])
def llm_health():
    try:
        reply = generate_completion("Say Hello in 3 languages English,Hindi,Japanese", max_token=50)
        return {
            "status":"ok",
            "reply": reply
        }
    
    except LLMServiceError as e:
        return {
            "status":"error",
            "message": str(e)
        }
