from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.retrieval.text_to_audio_retriever import retrieve_audio_from_text
from app.retrieval.audio_to_audio_retriever import retrieve_similar_audio
from app.retrieval.audio_to_text_retriever import retrieve_text_from_audio
from app.retrieval.audio_to_image_retriever import retrieve_image_from_audio
from app.utils.cloudinary_audio import upload_audio

router = APIRouter(prefix="/api/search/audio", tags=["Audio Search"])

MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/mp4",
    "audio/webm",
    "video/mp4",
    "video/webm",
}


class TextToAudioRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/text_to_audio")
def search_audio_from_text(
    req: TextToAudioRequest,
    current_user=Depends(get_current_user),
):
    """
    Search for audio files using text query.
    Queries are embedded and matched against audio transcripts.
    """
    results = retrieve_audio_from_text(
        query=req.query,
        owner_id=current_user.id,
        top_k=req.top_k,
    )

    # Filter by score threshold (similar to text search)
    MIN_SCORE = 0.25 if len(req.query.split()) <= 2 else 0.28
    filtered = [r for r in results if r["score"] >= MIN_SCORE]

    return {
        "query": req.query,
        "top_k": req.top_k,
        "results": filtered or results,  # Fallback if all filtered out
    }


@router.post("/audio_to_audio")
async def search_similar_audio(
    file: UploadFile = File(...),
    top_k: int = Form(5),
    user=Depends(get_current_user),
):
    """
    Find similar audio files by uploading an audio sample.
    Transcribes the query audio and matches against indexed transcripts.
    """
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported audio type")

    audio_bytes = await file.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=413, detail="Audio file too large")
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # Upload to temporary storage for processing
    audio_url = upload_audio(
        file_bytes=audio_bytes,
        filename=file.filename,
        owner_id=user.id,
        temp=True,  # Temporary upload for search
    )

    results = retrieve_similar_audio(
        audio_url=audio_url,
        owner_id=user.id,
        top_k=top_k,
    )

    # Filter by threshold
    MIN_SCORE = 0.30
    filtered = [r for r in results if r["score"] >= MIN_SCORE]

    return {
        "query_type": "audio_to_audio",
        "query_audio": audio_url,
        "results": filtered or results,
    }


@router.post("/audio_to_text")
async def search_text_from_audio(
    file: UploadFile = File(...),
    top_k: int = Form(5),
    user=Depends(get_current_user),
):
    """
    Search text documents using audio query.
    Transcribes audio and searches text collection.
    """
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported audio type")

    audio_bytes = await file.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=413, detail="Audio file too large")
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # Upload to temporary storage
    audio_url = upload_audio(
        file_bytes=audio_bytes,
        filename=file.filename,
        owner_id=user.id,
        temp=True,
    )

    results = retrieve_text_from_audio(
        audio_url=audio_url,
        owner_id=user.id,
        top_k=top_k,
    )

    # Filter by threshold
    MIN_SCORE = 0.28
    filtered = [r for r in results if r["score"] >= MIN_SCORE]

    return {
        "query_type": "audio_to_text",
        "query_audio": audio_url,
        "results": filtered or results,
    }

@router.post("/audio_to_image")
async def search_image_from_audio(
    file: UploadFile = File(...),
    top_k: int = Form(5),
    user=Depends(get_current_user),
):
    """
    Search image documents using audio query. 
    """
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported audio type")

    audio_bytes = await file.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=413, detail="Audio file too large")
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # Upload to temporary storage
    audio_url = upload_audio(
        file_bytes=audio_bytes,
        filename=file.filename,
        owner_id=user.id,
        temp=True,
    )

    results = retrieve_image_from_audio(
        audio_url=audio_url,
        owner_id=user.id,
        top_k=top_k,
    )

    # Filter by threshold
    MIN_SCORE = 0.28
    filtered = [r for r in results if r["score"] >= MIN_SCORE]

    return {
        "query_type": "audio_to_image",
        "query_audio": audio_url,
        "results": filtered or results,
    }