from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from app.utils.cloudinary_audio import upload_audio
from app.auth.dependencies import get_current_user
from app.asr.orchestrator import transcribe_audio
from app.ingestion.audio_indexer import index_audio
from app.utils.upload_validation import validate_audio_upload
import uuid 
from datetime import datetime

router =  APIRouter(prefix = "/api/audio",tags = ["Upload Audio"])

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
    """
    Upload and index an audio file.
    
    Validates:
    - File type (MP3, WAV, MP4, WEBM, etc.)
    - File size (max 100 MB)
    - File not empty
    - Minimum file size (10 KB)
    
    Then:
    - Transcribes audio (background task)
    - Indexes transcript into Qdrant
    
    Args:
        background_tasks: FastAPI background task handler
        file: Audio file to upload
        user: Authenticated user
        
    Returns:
        dict: File metadata and processing status
        
    Raises:
        HTTPException 400: Invalid/empty file
        HTTPException 413: File too large
        HTTPException 415: Invalid MIME type
    """
    audio_bytes = await file.read()
    
    # Validate upload
    validation = validate_audio_upload(audio_bytes, file.content_type, file.filename)
    
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

