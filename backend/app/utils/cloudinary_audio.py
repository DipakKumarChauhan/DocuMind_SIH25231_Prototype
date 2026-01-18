import cloudinary
import cloudinary.uploader
import uuid

def upload_audio(
        file_bytes: bytes,
        filename: str,
        owner_id: str,
        temp:bool = True
)-> str:
    """
    Upload audio to Cloudinary.
    temp=True → chat/search uploads
    temp=False → permanent dataset uploads
    """

    folder = (
        f"sih/audio/temp/{owner_id}"
        if temp
        else f"sih/audio/dataset/{owner_id}"
    )

    public_id = str(uuid.uuid4())

    result = cloudinary.uploader.upload(
        file_bytes,
        resource_type="video",
        folder=folder,
        public_id=public_id,
        overwrite=True,
    )

    return result["secure_url"]
    # return result


########### TO Upload Temp Audio #############
def upload_temp_audio(file_bytes: bytes, filename: str) -> str:
    """
    Uploads audio to Cloudinary as TEMP file for chat sessions.
    Returns secure URL.
    """
    res = cloudinary.uploader.upload(
        file_bytes,
        public_id=f"temp/chat/{filename}",
        resource_type="video",
        overwrite=True,
    )
    return res["secure_url"]


########### DELETE TEMP ASSETS #############
def delete_asset_by_url(asset_url: str):
    """
    Deletes Cloudinary asset using its public_id extracted from URL.
    Safe for audio/video files.
    Failure-tolerant: logs warning if deletion fails.
    
    Args:
        asset_url: Secure Cloudinary URL
    """
    try:
        if not asset_url or "cloudinary.com" not in asset_url:
            return
        
        parts = asset_url.split("/upload/")
        if len(parts) < 2:
            return
        
        path_with_ext = parts[1]
        
        # Remove version prefix (v{number}/) if present
        # Example: "v123/temp/chat/filename.mp3" → "temp/chat/filename.mp3"
        if path_with_ext.startswith("v") and "/" in path_with_ext:
            version_end = path_with_ext.index("/")
            path_with_ext = path_with_ext[version_end + 1:]
        
        # Remove file extension
        public_id = ".".join(path_with_ext.split(".")[:-1])
        
        result = cloudinary.uploader.destroy(public_id, invalidate=True)
        
        if result.get("result") == "ok":
            print(f"[INFO] Deleted temp asset: {public_id}")
        else:
            print(f"[WARN] Asset deletion returned non-ok status for {public_id}: {result}")
            
    except Exception as e:
        print(f"[WARN] Failed to delete asset {asset_url}: {e}")