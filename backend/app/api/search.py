from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
from app.retrieval.text_retriever import retrieve_text_chunks   

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
