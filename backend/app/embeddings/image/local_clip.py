from transformers import CLIPProcessor, CLIPModel
import torch
import requests
from PIL import Image
from io import BytesIO
from app.config import settings

_model = None
_processor = None

def _load():
    global _model,_processor
    if _model is None:
        # If a local model folder is provided, load from disk without network.
        if settings.CLIP_MODEL_PATH:
            _model = CLIPModel.from_pretrained(settings.CLIP_MODEL_PATH, local_files_only=True)
            _processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL_PATH, local_files_only=True)
        else:
            # Use central cache dir for HF downloads; it won't redownload if present
            _model = CLIPModel.from_pretrained(
                "openai/clip-vit-base-patch32",
                cache_dir=settings.MODEL_CACHE_DIR
            )
            _processor = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32",
                cache_dir=settings.MODEL_CACHE_DIR
            )
        _model.eval()
    
def embed_image_local(image_url:str)-> list[float]:
    """Fetch an image, process it with local CLIP model, and return image embedding."""
    _load()
    
    image = Image.open(BytesIO(requests.get(image_url, timeout=20).content)).convert("RGB")
    
                #     requests.get(image_url, timeout=20) → downloads image

                # .content → raw bytes

                # BytesIO(...) → wraps bytes like a file

                # Image.open(...) → loads as image object

                # .convert("RGB") → ensures 3-channel color format
    
    inputs = _processor(images=image, return_tensors="pt") # this line sends the image to CLIP preprocessing pipeline and return pyTorch Tensors "pt"

    with torch.no_grad():
        emb = _model.get_image_features(**inputs)
    
    emb = emb / emb.norm(dim=-1,keepdim=True)

    return emb.squeeze().tolist()



