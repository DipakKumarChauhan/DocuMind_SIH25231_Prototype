
# This file calls a remote API to get image embeddings instead of using a local model.
# Call When have a CLIP embedding API available.

import requests
from app.config import settings

def embed_image_remote(image_url: str) -> list[float] | None:
    if not settings.IMAGE_EMBEDDING_API_URL:
        return None

    response = requests.post(
        settings.IMAGE_EMBEDDING_API_URL,
        headers={"Authorization": f"Bearer {settings.IMAGE_EMBEDDING_API_KEY}"},
        json={"image_url": image_url},
        timeout=15,
    )

    response.raise_for_status()
    return response.json()["embedding"]
