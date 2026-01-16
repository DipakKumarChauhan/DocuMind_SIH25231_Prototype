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