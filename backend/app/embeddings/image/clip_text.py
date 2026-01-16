from transformers import CLIPProcessor, CLIPModel
import torch
from app.config import settings

_model = None
_processor = None

def _load():
    global _model, _processor
    if _model is None:
        # Load from local path or HF cache, same as image embedding
        if settings.CLIP_MODEL_PATH:
            _model = CLIPModel.from_pretrained(settings.CLIP_MODEL_PATH, local_files_only=True)
            _processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL_PATH, local_files_only=True)
        else:
            # Use central cache dir; HF will reuse local files when present
            _model = CLIPModel.from_pretrained(
                "openai/clip-vit-base-patch32",
                cache_dir=settings.MODEL_CACHE_DIR
            )
            _processor = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32",
                cache_dir=settings.MODEL_CACHE_DIR
            )
        _model.eval()

def embed_text_clip(text: str) -> list[float]:
    """
    Encode text using CLIP's text encoder.
    Returns 512-dim embedding in the same space as CLIP image embeddings.
    """
    _load()
    
    # Tokenize and process text
    inputs = _processor(text=text, return_tensors="pt", padding=True, truncation=True)
    
    with torch.no_grad():
        text_features = _model.get_text_features(**inputs)
    
    # L2 normalize
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    return text_features.squeeze().tolist()
