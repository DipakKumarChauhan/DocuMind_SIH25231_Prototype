from fastapi import APIRouter,UploadFile,File,HTTPException,Depends
from pathlib import Path
from uuid import uuid4
from app.utils.cloudinary import upload_image
from app.auth.dependencies  import get_current_user 
from app.ingestion.image_indexer import index_image
from app.utils.upload_validation import validate_image_upload

router = APIRouter(prefix="/api/upload",tags=["upload"])

@router.post("/image")
async def upload_image_api(
    file:UploadFile = File(...),
    current_user= Depends(get_current_user) 
):
    """
    Upload and index an image file.
    
    Validates:
    - File type (JPEG, PNG, GIF, WEBP)
    - File size (max 50 MB)
    - File not empty
    - Minimum file size (1 KB)
    
    Args:
        file: Image file to upload
        current_user: Authenticated user
        
    Returns:
        dict: File metadata and URL
        
    Raises:
        HTTPException 400: Invalid file
        HTTPException 413: File too large
        HTTPException 415: Invalid MIME type
    """
    file_bytes = await file.read()
    
    # Validate upload
    validation = validate_image_upload(file_bytes, file.content_type, file.filename)

    file_id = str(uuid4())
    public_id =  f"{current_user.id}/{file_id}" 

    cloudinary_result = upload_image(
        file_bytes=file_bytes,
        public_id=public_id,
        )
    image_url = cloudinary_result["secure_url"]
    file_id = cloudinary_result["public_id"]
    
    try:
        index_image(
        image_url=image_url,
        owner_id=current_user.id,
        file_id=file_id,
    )
    except Exception as e:
        raise HTTPException(status_code=500,detail="Failed to index image")
    return {
        "file_id": file_id,
        "image_url": cloudinary_result["secure_url"],
        "width": cloudinary_result["width"],
        "height": cloudinary_result["height"],
        "format": cloudinary_result["format"],
        "owner_id": current_user.id,
    }



