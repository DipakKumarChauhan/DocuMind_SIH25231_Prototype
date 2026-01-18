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


########### DELETE TEMP ASSETS #############
def delete_asset_by_url(asset_url: str):
    """
    Deletes Cloudinary asset using its public_id extracted from URL.
    Safe for images and audio/video files.
    Failure-tolerant: logs warning if deletion fails.
    
    Example URL:
    https://res.cloudinary.com/<cloud>/image/upload/v123/temp/chat/abc.png
    
    Args:
        asset_url: Secure Cloudinary URL
    """
    try:
        # Extract public_id from URL
        # Format: https://res.cloudinary.com/{cloud}/{resource}/upload/{path}/{filename}
        if not asset_url or "cloudinary.com" not in asset_url:
            return
        
        # Split by upload/ and take everything after
        parts = asset_url.split("/upload/")
        if len(parts) < 2:
            return
        
        path_with_ext = parts[1]
        
        # Remove version prefix (v{number}/) if present
        # Example: "v123/temp/chat/filename.png" → "temp/chat/filename.png"
        if path_with_ext.startswith("v") and "/" in path_with_ext:
            version_end = path_with_ext.index("/")
            path_with_ext = path_with_ext[version_end + 1:]
        
        # Remove file extension
        public_id = ".".join(path_with_ext.split(".")[:-1])
        
        # Attempt deletion
        result = cloudinary.uploader.destroy(public_id, invalidate=True)
        
        if result.get("result") == "ok":
            print(f"[INFO] Deleted temp asset: {public_id}")
        else:
            print(f"[WARN] Asset deletion returned non-ok status for {public_id}: {result}")
            
    except Exception as e:
        print(f"[WARN] Failed to delete asset {asset_url}: {e}")