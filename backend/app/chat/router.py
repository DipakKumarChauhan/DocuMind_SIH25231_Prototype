# from app.retrieval.text_retriever import retrieve_text_chunks
# from app.retrieval.image_retriever import retrieve_images_from_text
# from app.retrieval.text_to_audio_retriever import retrieve_audio_from_text
# from app.retrieval.audio_to_text_retriever import retrieve_text_from_audio
# from app.retrieval.image_to_text_retriever import retrieve_text_from_image
# from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
# from app.chat.intent import classify_intent


# def route_query(normalized: dict):
#     """Route a normalized chat query to retrieval pipelines.

#     Produces keys expected by context builder:
#     - text, image, audio: retrievals based on text query
#     - image_text: OCR text extracted from uploaded image URL
#     - audio_text: transcript text extracted from uploaded audio URL
#     """
#     results = {
#         "text": [],
#         "image": [],
#         "audio": [],
#         "image_text": [],
#         "audio_text": [],
#     }

#     # 🔍 Intent classification
#     intent = classify_intent(normalized)
    
#     # ❌ Skip retrieval for chitchat (greetings, small talk)
#     if intent == "chitchat":
#         return results

#     # ❌ Skip retrieval for meta-questions (about chat history)
#     # These should use session history, not database
#     if intent == "meta":
#         return results

#     embedder = HFBgeM3Embedder()

#     # Text-driven retrievals
#     text = (normalized.get("text") or "").strip()
#     owner_id = normalized.get("owner_id")
#     if text:
#         results["text"] = retrieve_text_chunks(text, owner_id, embedder)
#         results["image"] = retrieve_images_from_text(text, owner_id)
#         results["audio"] = retrieve_audio_from_text(text, owner_id)

#     # Extract text from uploaded image/audio
#     image_url = normalized.get("image_url")
#     if image_url:
#         results["image_text"] = retrieve_text_from_image(image_url, owner_id)

#     audio_url = normalized.get("audio_url")
#     if audio_url:
#         results["audio_text"] = retrieve_text_from_audio(audio_url, owner_id)

#     return results
 
import asyncio
import time

from app.chat.intent import classify_intent

# Text-based
from app.retrieval.text_retriever import retrieve_text_chunks
from app.retrieval.image_retriever import retrieve_images_from_text
from app.retrieval.text_to_audio_retriever import retrieve_audio_from_text

# Image-based
from app.retrieval.image_to_image_retriever import retrieve_similar_images
from app.retrieval.image_to_text_retriever import retrieve_text_from_image
from app.retrieval.image_to_audio_retriever import retrieve_audio_from_image

# Audio-based
from app.retrieval.audio_to_audio_retriever import retrieve_similar_audio
from app.retrieval.audio_to_text_retriever import retrieve_text_from_audio
from app.retrieval.audio_to_image_retriever import retrieve_image_from_audio

from app.embeddings.hf_bge_m3 import HFBgeM3Embedder


TIMEOUT_SECONDS = 30


async def _with_timeout(func, *args, timeout: float = TIMEOUT_SECONDS):
    """Run sync retrieval in a thread with a hard timeout, returning [] on timeout."""
    try:
        result = await asyncio.wait_for(asyncio.to_thread(func, *args), timeout=timeout)
        return result if result else []
    except asyncio.TimeoutError:
        from app.config import settings
        if settings.LOG_RETRIEVAL:
            print(f"[RETRIEVAL] ⏱️ TIMEOUT ({timeout}s): {func.__name__}")
        return []


async def route_query(normalized: dict) -> dict:
    """
    Multimodal retrieval router.

    Rules:
    - Same-modality retrieval ALWAYS runs first
    - Cross-modal retrieval ALWAYS runs second
    - Text is semantic bridge, not a replacement
    """
    from app.config import settings
    
    results = {
        "text": [],
        "image": [],
        "audio": [],
    }

    owner_id = normalized["owner_id"]
    text = (normalized.get("text") or "").strip()
    image_url = normalized.get("image_url")
    audio_url = normalized.get("audio_url")

    # 🧠 Intent gating
    intent = classify_intent(normalized)
    if intent in {"chitchat", "meta"}:
        if settings.LOG_RETRIEVAL:
            print(f"[RETRIEVAL] ⏭️ Skipped (intent={intent})")
        return results

    embedder = HFBgeM3Embedder()

    # ==========================================================
    # 📝 TEXT QUERY PATH
    # ==========================================================
    if text:
        if settings.LOG_RETRIEVAL:
            print(f"[RETRIEVAL] 📝 Text query: '{text[:50]}...'")
        # Text → Text
        results["text"].extend(
            retrieve_text_chunks(text, owner_id, embedder)
        )

        # Text → Image
        results["image"].extend(
            retrieve_images_from_text(text, owner_id)
        )

        # Text → Audio
        results["audio"].extend(
            retrieve_audio_from_text(text, owner_id)
        )

    # ==========================================================
    # 🖼 IMAGE QUERY PATH
    # ==========================================================
    if image_url:
        if settings.LOG_RETRIEVAL:
            print(f"[RETRIEVAL] 🖼️ Image query")
        # Image → Image (PRIMARY)
        results["image"].extend(
            await _with_timeout(retrieve_similar_images, image_url, owner_id)
        )

        # Image → Text (OCR → text)
        results["text"].extend(
            await _with_timeout(retrieve_text_from_image, image_url, owner_id)
        )

        # Image → Audio (OCR → transcript)
        results["audio"].extend(
            await _with_timeout(retrieve_audio_from_image, image_url, owner_id)
        )

    # ==========================================================
    # 🔊 AUDIO QUERY PATH
    # ==========================================================
    if audio_url:
        if settings.LOG_RETRIEVAL:
            print(f"[RETRIEVAL] 🔊 Audio query")
        # Audio → Audio (PRIMARY)
        results["audio"].extend(
            await _with_timeout(retrieve_similar_audio, audio_url, owner_id)
        )

        # Audio → Text (transcript)
        results["text"].extend(
            await _with_timeout(retrieve_text_from_audio, audio_url, owner_id)
        )

        # Audio → Image (transcript → OCR)
        results["image"].extend(
            await _with_timeout(retrieve_image_from_audio, audio_url, owner_id)
        )

    return results
