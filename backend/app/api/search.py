from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
from app.retrieval.text_retriever import retrieve_text_chunks  
from app.rag.text_rag import generate_rag_answer 
from app.schemas.api import AskRequest

router = APIRouter(prefix="/api",tags=['Search'])

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/search/text")
def search_text(
    req: SearchRequest,
    current_user= Depends(get_current_user)
):
    embedder = HFBgeM3Embedder()

    hits = retrieve_text_chunks(
        query=req.query,
        owner_id=current_user.id,
        embedder=embedder,
        top_k=req.top_k,
    )

    return {
        "query": req.query,
        "top_k": req.top_k,
        "results": hits,
    }

@router.post("/ask")
def ask_question(payload: AskRequest):
    embedder = HFBgeM3Embedder()
    chunks = retrieve_text_chunks(
        query=payload.query,
        owner_id=payload.owner_id,
    
    
        embedder=embedder,
        top_k=5,
    )

    rag_result = generate_rag_answer(
        query=payload.query,
        chunks=chunks,
    )

    return {
        "query": payload.query,
        "answer": rag_result["answer"],
        "citations": rag_result["citations"],
    }
