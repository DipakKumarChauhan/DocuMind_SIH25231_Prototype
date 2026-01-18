from app.utils.cloudinary import upload_temp_image
from app.utils.cloudinary_audio import upload_temp_audio
from app.asr.orchestrator import transcribe_audio
from app.embeddings.image.orchestrator import embed_image


async def normalize_chat_input(
        message: str | None,
        image,
        audio,
        owner_id: str,
        session: dict | None = None,
):
    text = message or ""
    image_url = None
    audio_url = None

    if image :
        image_bytes = await image.read()
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
        except Exception as e:
            # Fail-safe: don't block chat turn if OCR fails
            print(f"[WARN] OCR extraction failed for {image_url}: {e}")

    if audio :
        audio_bytes = await audio.read()
        audio_url = upload_temp_audio(audio_bytes, audio.filename)
        # Track temp audio in session
        if session:
            session["temp_assets"]["audio"].append(audio_url)
        transcription_result = transcribe_audio(audio_url)
        text += " " + transcription_result["transcript"] 

    return {
        "text": text.strip(),
        "image_url": image_url,
        "audio_url": audio_url,
        "owner_id": owner_id,
    }


