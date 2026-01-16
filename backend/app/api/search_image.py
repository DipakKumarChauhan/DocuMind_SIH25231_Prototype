from fastapi import APIRouter , Depends,UploadFile, File,Form, HTTPException
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.retrieval.image_retriever import retrieve_images_from_text
from app.retrieval.image_to_image_retriever import retrieve_similar_images
from app.retrieval.image_to_text_retriever import retrieve_text_from_image
from app.retrieval.image_to_audio_retriever import retrieve_audio_from_image
from app.utils.cloudinary import upload_temp_image

router = APIRouter(prefix = "/api/search/image", tags = ["Image Search"])

MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

class ImageSearchRequest(BaseModel):
    query: str
    top_k: int = 5

# ### Image to Text Search Endpoint Class ###
# class ImageSearchRequestImagetoImage(BaseModel):
#     image_url: str
#     top_k: int = 5

@router.post("/text_to_image_search")
def search_image(
    req: ImageSearchRequest,
    current_user = Depends(get_current_user),
):
    results = retrieve_images_from_text(
        query = req.query,
        owner_id = current_user.id,
        top_k = req.top_k,
    )

    return {
        "query": req.query,
        "results": results,
    }

### Image to Image Search Endpoint ###
@router.post("/image_to_image_search")
async def image_to_image_search(
    file: UploadFile = File(...),
    top_k: int = Form(5),
    user=Depends(get_current_user),
):
    image_url = await _validate_and_upload_image(file)

    results = retrieve_similar_images(
        image_url = image_url,
        owner_id = user.id,
        top_k = top_k,
    )

    return {
        "query_type": "image_to_image",
        "query_image": image_url,
        "results": results,
    }

@router.post("/image_to_text_search")

async def image_to_text_search(
    file: UploadFile = File(...),
    top_k: int = Form(5),
    user=Depends(get_current_user),
):
    image_url = await _validate_and_upload_image(file)

    results = retrieve_text_from_image(
        image_url = image_url,
        owner_id = user.id,
        top_k = top_k,
    )
    if not results:
        return {
            "query_type": "image_to_text",
            "query_image": image_url,
            "results": [],
            "warning": "No relevant matches found"
        }


    return {
        "query_type": "image_to_text",
        "query_image": image_url,
        "results": results,
    }

@router.post("/image_to_audio_search")
async def image_to_audio_search(
    file: UploadFile = File(...),
    top_k: int = Form(5),
    user=Depends(get_current_user),
):
    image_url = await _validate_and_upload_image(file)

    results = retrieve_audio_from_image(
        image_url = image_url,
        owner_id = user.id,
        top_k = top_k,
    )

    # Filter by score threshold (consistent with audio search endpoints)
    MIN_SCORE = 0.28
    filtered = [r for r in results if r["score"] >= MIN_SCORE]

    return {
        "query_type": "image_to_audio",
        "query_image": image_url,
        "results": filtered or results,  # Fallback if all filtered out
    }




async def _validate_and_upload_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, "Unsupported file type")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(413, "Image too large")
    if not image_bytes:
        raise HTTPException(400, "Empty file")

    # Upload once after validation to avoid double reads.
    return upload_temp_image(
        file_bytes=image_bytes,
        filename=file.filename,
    )

