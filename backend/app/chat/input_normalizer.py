from app.utils.cloudinary import upload_temp_image
from app.utils.cloudinary_audio import upload_temp_audio
from app.asr.orchestrator import transcribe_audio
from app.embeddings.image.orchestrator import embed_image
from app.utils.upload_validation import validate_chat_upload
from fastapi import HTTPException


async def normalize_chat_input(
        message: str | None,
        image,
        audio,
        owner_id: str,
        session: dict | None = None,
):
    """
    Normalize and validate chat input.
    
    Accepts optional text, image, and/or audio.
    Validates files, extracts content, generates embeddings.
    
    Args:
        message: Text query
        image: Image file (optional)
        audio: Audio file (optional)
        owner_id: User ID for tracking
        session: Chat session dict for temp asset tracking
        
    Returns:
        dict: Normalized input with extracted text
        
    Raises:
        HTTPException: If validation fails
    """
    text = message or ""
    image_url = None
    audio_url = None

    if image:
        image_bytes = await image.read()
        
        # Validate image upload
        try:
            validation = validate_chat_upload(image_bytes, image.content_type, image.filename, "image")
            print(f"[DEBUG] Image validated: {validation}")
        except HTTPException as e:
            print(f"[ERROR] Image validation failed: {e.detail}")
            raise
        
        image_url = upload_temp_image(image_bytes, image.filename)
        # Track temp image in session
        if session:
            session["temp_assets"]["images"].append(image_url)
        
        # Generate OCR immediately so the uploaded image contributes to context
        try:
            emb = embed_image(image_url)
            ocr_text = emb.get("ocr_text")
            if ocr_text and len(ocr_text.strip()) > 0:
                text += " " + ocr_text
                print(f"[DEBUG] OCR extracted {len(ocr_text)} chars")
        except Exception as e:
            # Fail-safe: don't block chat turn if OCR fails
            print(f"[WARN] OCR extraction failed for {image_url}: {e}")

    if audio:
        audio_bytes = await audio.read()
        
        # Validate audio upload
        try:
            validation = validate_chat_upload(audio_bytes, audio.content_type, audio.filename, "audio")
            print(f"[DEBUG] Audio validated: {validation}")
        except HTTPException as e:
            print(f"[ERROR] Audio validation failed: {e.detail}")
            raise
        
        audio_url = upload_temp_audio(audio_bytes, audio.filename)
        # Track temp audio in session
        if session:
            session["temp_assets"]["audio"].append(audio_url)
        
        # Transcribe audio
        try:
            transcription_result = transcribe_audio(audio_url)
            transcript = transcription_result.get("transcript", "")
            if transcript:
                text += " " + transcript
                print(f"[DEBUG] Audio transcribed: {len(transcript)} chars")
        except Exception as e:
            print(f"[WARN] Audio transcription failed for {audio_url}: {e}")
            raise HTTPException(status_code=500, detail="Audio transcription failed")

    return {
        "text": text.strip(),
        "image_url": image_url,
        "audio_url": audio_url,
        "owner_id": owner_id,
    }


