from fastapi import APIRouter,UploadFile,File,HTTPException,Depends
from pathlib import Path
from uuid import uuid4
from app.utils.cloudinary import upload_image
from app.auth.dependencies  import get_current_user 
router = APIRouter(prefix="/api/upload",tags=["upload"])

ALLOWED_IMAGE_TYPES = ["image/jpeg","image/png","image/gif","image/webp"]

@router.post("/image")

async def upload_image_api(
    file:UploadFile = File(...),
    current_user= Depends(get_current_user) 
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400,detail="Invalid image type")

    file_bytes = await file.read()

    file_id = str(uuid4())
    public_id =  f"{current_user.id}/{file_id}" 

    cloudinary_result = upload_image(
        file_bytes=file_bytes,
        public_id=public_id,
        )
    return {
        "file_id": file_id,
        "image_url": cloudinary_result["secure_url"],
        "width": cloudinary_result["width"],
        "height": cloudinary_result["height"],
        "format": cloudinary_result["format"],
        "owner_id": current_user.id,
    }



