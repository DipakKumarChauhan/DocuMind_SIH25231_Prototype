from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from app.utils.cloudinary_audio import upload_audio
from app.auth.dependencies import get_current_user
from app.asr.orchestrator import transcribe_audio
from app.ingestion.audio_indexer import index_audio
import uuid 
from datetime import datetime

router =  APIRouter(prefix = "/api/audio",tags = ["Upload Audio"])

MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100 MB

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/mp4",
    "audio/webm",
    "video/mp4",  # MP4 files are often uploaded with video MIME type
    "video/webm",
}

# Implementation 3: Background processing helper
def process_audio_background(audio_url: str, owner_id: str, file_id: str):
    """Transcribe and index audio in the background."""
    try:
        transcription_result = transcribe_audio(audio_url)
        transcript = transcription_result.get("transcript", "")
        segments = transcription_result.get("segments", [])

        index_audio(
            audio_url=audio_url,
            owner_id=owner_id,
            file_id=file_id,
            transcript=transcript,
            timestamps=segments,
        )
    except Exception as e:
        # Minimal logging; consider replacing with structured logging
        print(f"Background processing failed for {file_id}: {e}")

@router.post("/upload")
async def upload_audio_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported audio type.")
    
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file.")
    
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=400, detail="Audio file exceeds maximum size limit.")
    
    audio_url = upload_audio(
        file_bytes=audio_bytes,
        filename=file.filename,
        owner_id=user.id,
        temp=False,
    )

    # --- Legacy synchronous processing (commented for easy revert) ---
    # try:
    #     transcription_result = transcribe_audio(audio_url)
    #     transcript = transcription_result["transcript"]
    #     segments = transcription_result.get("segments", [])
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Audio transcription failed: {str(e)}"
    #     )
    #
    # file_id = str(uuid.uuid4())
    # try:
    #     index_audio(
    #         audio_url=audio_url,
    #         owner_id=user.id,
    #         file_id=file_id,
    #         transcript=transcript,
    #         timestamps=segments,
    #     )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Indexing failed: {str(e)}"
    #     )
    #
    # return {
    #     "audio_url": audio_url,
    #     "filename": file.filename,
    #     "file_id": file_id,
    #     "transcript": transcript,
    #     "status": "indexed",
    #     "created_at": datetime.utcnow().isoformat(),
    # }

    # Schedule background processing
    file_id = str(uuid.uuid4())
    background_tasks.add_task(
        process_audio_background,
        audio_url=audio_url,
        owner_id=user.id,
        file_id=file_id,
    )

    # Return early with processing status
    return {
        "audio_url": audio_url,
        "filename": file.filename,
        "file_id": file_id,
        "status": "processing",
        "message": "Audio uploaded successfully. Transcription and indexing in progress.",
        "created_at": datetime.utcnow().isoformat(),
    }

