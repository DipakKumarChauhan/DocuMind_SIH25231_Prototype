import cloudinary
import cloudinary.uploader
from app.config import settings    

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

def upload_image(file_bytes:bytes,public_id:str) ->dict:
   """
    Upload image to Cloudinary and return metadata
    """
   
   result =  cloudinary.uploader.upload(
      file_bytes,
      public_id = public_id,
      folder= "sih/images",
      resource_type= "image"
   )
   return result


########### TO Upload Temp Image #############
def upload_temp_image(file_bytes: bytes, filename: str) -> str:
    """
    Uploads image to Cloudinary as TEMP file.
    Returns secure URL.
    """
    res = cloudinary.uploader.upload(
        file_bytes,
        public_id=f"temp/chat/{filename}",
        resource_type="image",
        overwrite=True,
    )
    return res["secure_url"]