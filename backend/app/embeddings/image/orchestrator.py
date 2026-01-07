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
      ocr_text: str | None
    }
    """

    mode = settings.IMAGE_EMBEDDING_MODE

    # ===== ADDED: Explicit OCR-only mode =====
    # When IMAGE_EMBEDDING_MODE is set to "ocr", skip model inference and
    # compute an embedding purely from OCR-extracted text. This avoids any
    # model downloads and can be useful in constrained environments.
    if mode == "ocr":
        ocr_text = extract_text_from_image(image_url)
        text_content = " ".join([block.get("text", "") for block in ocr_text if isinstance(block, dict)])
        text_embedder = _get_text_embedder()
        vec = text_embedder.embed_query(text_content)
        return {
            "vector": vec,
            "source": "ocr",
            "ocr_text": text_content,
        }
    # ===== END ADDED =====

    # ---------- REMOTE ----------
    if mode in ("auto", "remote"):
        try:
            vec = embed_image_remote(image_url)
            if vec:
                return {
                    "vector": vec,
                    "source": "remote",
                    "ocr_text": None,
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
                "ocr_text": None,
            }
        except Exception:
            if mode == "local":
                raise

    # ---------- OCR FALLBACK ----------
    ocr_text = extract_text_from_image(image_url)
    # Extract just the text from OCR blocks
    text_content = " ".join([block.get("text", "") for block in ocr_text if isinstance(block, dict)])
    
    text_embedder = _get_text_embedder()
    vec = text_embedder.embed_query(text_content)

    return {
        "vector": vec,
        "source": "ocr_fallback",
        "ocr_text": text_content,
    }
