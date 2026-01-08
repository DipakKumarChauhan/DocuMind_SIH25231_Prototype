from app.config import settings
from app.embeddings.image.local_clip import embed_image_local
from app.embeddings.image.remote_clip import embed_image_remote
from app.ocr.google_vision import extract_text_from_image
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder

# Initialize text embedder
_text_embedder = None

def _get_text_embedder():
    global _text_embedder
    if _text_embedder is None:
        _text_embedder = HFBgeM3Embedder()
    return _text_embedder

def embed_image(image_url: str) -> dict:
    """
    Returns:
    {
      vector: List[float],
      source: "remote" | "local" | "ocr" | "ocr_fallback",
      ocr_text: str | None,
      ocr_blocks: list[dict] | None
    }
    """

    mode = settings.IMAGE_EMBEDDING_MODE

    # ===== ADDED: Explicit OCR-only mode =====
    # When IMAGE_EMBEDDING_MODE is set to "ocr", skip model inference and
    # compute an embedding purely from OCR-extracted text. This avoids any
    # model downloads and can be useful in constrained environments.
    if mode == "ocr":
        ocr_blocks = extract_text_from_image(image_url)  # list of {text, bounding_box}
        text_content = " ".join([block.get("text", "") for block in ocr_blocks if isinstance(block, dict)])
        text_embedder = _get_text_embedder()
        vec = text_embedder.embed_query(text_content)
        return {
            "vector": vec,
            "source": "ocr",
            "ocr_text": text_content,
            "ocr_blocks": ocr_blocks,
        }
    # ===== END ADDED =====

    # Extract OCR once and reuse for all branches to avoid repeated calls
    # This provides searchable text alongside visual embeddings
    ocr_blocks = extract_text_from_image(image_url)  # list of {text, bounding_box}
    ocr_text = " ".join([block.get("text", "") for block in ocr_blocks if isinstance(block, dict)])

    # ---------- REMOTE ----------
    if mode in ("auto", "remote"):
        try:
            vec = embed_image_remote(image_url)
            if vec:
                return {
                    "vector": vec,
                    "source": "remote",
                    "ocr_text": ocr_text or None,
                    "ocr_blocks": ocr_blocks or None,
                }
        except Exception:
            if mode == "remote":
                raise

    # ---------- LOCAL ----------
    if mode in ("auto", "local"):
        try:
            vec = embed_image_local(image_url)
            return {
                "vector": vec,
                "source": "local",
                "ocr_text": ocr_text or None,
                "ocr_blocks": ocr_blocks or None,
            }
        except Exception:
            if mode == "local":
                raise

    # ---------- OCR FALLBACK ----------
    # Use precomputed OCR text for fallback to avoid additional OCR calls
    text_content = ocr_text
    
    text_embedder = _get_text_embedder()
    vec = text_embedder.embed_query(text_content)

    return {
        "vector": vec,
        "source": "ocr_fallback",
        "ocr_text": text_content,
        "ocr_blocks": ocr_blocks or None,
    }
