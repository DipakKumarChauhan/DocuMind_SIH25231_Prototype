
##################### Imports #####################

from fastapi import FastAPI
from app.config import settings
from app.middleware.cors import setup_cors
from app.db.collections import create_collections
from app.db.qdrant_client import get_qdrant_client
from app.rag.groq_client import generate_completion, LLMServiceError

################## Importing API routers ##################
from app.api.upload_admin import route as upload_router




app = FastAPI(
    title="Multimodal RAG Back-end",
    version="0.1.0",
)

#injecing Cors Middleware
setup_cors(app)

# Registering API routers 
app.include_router(upload_router)

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
