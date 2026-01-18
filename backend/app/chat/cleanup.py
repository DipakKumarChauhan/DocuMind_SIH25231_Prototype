"""
Cleanup module for temporary session assets.

Handles deletion of temporary images and audio files uploaded during chat.
"""

from app.utils.cloudinary import delete_asset_by_url as delete_image
from app.utils.cloudinary_audio import delete_asset_by_url as delete_audio


def cleanup_temp_assets(session: dict):
    """
    Deletes all temporary assets associated with a chat session.
    
    Iterates through session["temp_assets"] and removes:
    - Temporary images uploaded during chat
    - Temporary audio files uploaded during chat
    
    Clears the temp_assets list after cleanup.
    
    Args:
        session: Chat session dict containing "temp_assets" key
        
    Returns:
        None (side effects: deletes from Cloudinary, clears session tracking)
    """
    if not session or "temp_assets" not in session:
        return
    
    assets = session.get("temp_assets", {})
    
    # Delete images
    for image_url in assets.get("images", []):
        if image_url:
            delete_image(image_url)
    
    # Delete audio
    for audio_url in assets.get("audio", []):
        if audio_url:
            delete_audio(audio_url)
    
    # Clear tracking after cleanup
    session["temp_assets"] = {
        "images": [],
        "audio": [],
    }
    
    print(f"[INFO] Cleaned up {len(assets.get('images', []))} images and {len(assets.get('audio', []))} audio files")
