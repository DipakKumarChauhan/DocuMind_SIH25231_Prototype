"""
Upload validation utilities for safe file handling.

Validates:
- File size limits
- MIME types
- Empty files
- Corrupted uploads
"""

from fastapi import HTTPException
from typing import Set


# Constants
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_PDF_SIZE = 200 * 1024 * 1024  # 200 MB

ALLOWED_IMAGE_MIMES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}

ALLOWED_AUDIO_MIMES = {
    "audio/mpeg",
    "audio/wav",
    "audio/mp4",
    "audio/webm",
    "audio/ogg",
    "audio/aac",
    "audio/flac",
    "video/mp4",  # MP4 files often uploaded with video MIME type
    "video/webm",
}

ALLOWED_DOCUMENT_MIMES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/msword",  # .doc
}


def validate_image_upload(file_bytes: bytes, content_type: str, filename: str) -> dict:
    """
    Validate image file upload.
    
    Args:
        file_bytes: Raw file bytes
        content_type: MIME type from UploadFile
        filename: Original filename
        
    Returns:
        dict: {"valid": bool, "message": str}
        
    Raises:
        HTTPException: If validation fails
    """
    # Check MIME type
    if content_type not in ALLOWED_IMAGE_MIMES:
        raise HTTPException(
            status_code=415,
            detail=f"Invalid image type: {content_type}. Allowed types: {', '.join(ALLOWED_IMAGE_MIMES)}"
        )
    
    # Check empty file
    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Image file is empty"
        )
    
    # Check file size
    if len(file_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Image file exceeds maximum size ({MAX_IMAGE_SIZE / 1024 / 1024:.0f} MB)"
        )
    
    # Check minimum size (at least 1KB for valid image)
    if len(file_bytes) < 1024:
        raise HTTPException(
            status_code=400,
            detail="Image file too small (must be at least 1 KB)"
        )
    
    return {
        "valid": True,
        "size_mb": round(len(file_bytes) / 1024 / 1024, 2),
        "filename": filename
    }


def validate_audio_upload(file_bytes: bytes, content_type: str, filename: str) -> dict:
    """
    Validate audio file upload.
    
    Args:
        file_bytes: Raw file bytes
        content_type: MIME type from UploadFile
        filename: Original filename
        
    Returns:
        dict: {"valid": bool, "message": str}
        
    Raises:
        HTTPException: If validation fails
    """
    # Check MIME type
    if content_type not in ALLOWED_AUDIO_MIMES:
        raise HTTPException(
            status_code=415,
            detail=f"Invalid audio type: {content_type}. Allowed types: {', '.join(ALLOWED_AUDIO_MIMES)}"
        )
    
    # Check empty file
    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Audio file is empty"
        )
    
    # Check file size
    if len(file_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file exceeds maximum size ({MAX_AUDIO_SIZE / 1024 / 1024:.0f} MB)"
        )
    
    # Check minimum size (at least 10KB for valid audio)
    if len(file_bytes) < 10 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Audio file too small (must be at least 10 KB)"
        )
    
    return {
        "valid": True,
        "size_mb": round(len(file_bytes) / 1024 / 1024, 2),
        "filename": filename
    }


def validate_document_upload(file_bytes: bytes, content_type: str, filename: str) -> dict:
    """
    Validate document (PDF/DOCX) file upload.
    
    Args:
        file_bytes: Raw file bytes
        content_type: MIME type from UploadFile
        filename: Original filename
        
    Returns:
        dict: {"valid": bool, "message": str}
        
    Raises:
        HTTPException: If validation fails
    """
    # Check MIME type
    if content_type not in ALLOWED_DOCUMENT_MIMES:
        raise HTTPException(
            status_code=415,
            detail=f"Invalid document type: {content_type}. Allowed types: PDF, DOCX"
        )
    
    # Check empty file
    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Document file is empty"
        )
    
    # Check file size
    if len(file_bytes) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Document file exceeds maximum size ({MAX_PDF_SIZE / 1024 / 1024:.0f} MB)"
        )
    
    # Check minimum size (at least 1KB for valid document)
    if len(file_bytes) < 1024:
        raise HTTPException(
            status_code=400,
            detail="Document file too small (must be at least 1 KB)"
        )
    
    # Magic byte validation for PDF
    if filename.lower().endswith(".pdf"):
        if not file_bytes.startswith(b"%PDF"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file (corrupted or not a valid PDF)"
            )
    
    # Magic byte validation for DOCX (ZIP archive)
    if filename.lower().endswith(".docx"):
        if not file_bytes.startswith(b"PK\x03\x04"):  # ZIP magic bytes
            raise HTTPException(
                status_code=400,
                detail="Invalid DOCX file (corrupted or not a valid DOCX)"
            )
    
    return {
        "valid": True,
        "size_mb": round(len(file_bytes) / 1024 / 1024, 2),
        "filename": filename
    }


def validate_chat_upload(
    file_bytes: bytes,
    content_type: str,
    filename: str,
    file_type: str  # "image" or "audio"
) -> dict:
    """
    Validate file upload in chat context (temporary uploads).
    
    Args:
        file_bytes: Raw file bytes
        content_type: MIME type
        filename: Original filename
        file_type: "image" or "audio"
        
    Returns:
        dict: Validation result
        
    Raises:
        HTTPException: If validation fails
    """
    if file_type == "image":
        return validate_image_upload(file_bytes, content_type, filename)
    elif file_type == "audio":
        return validate_audio_upload(file_bytes, content_type, filename)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown file type: {file_type}"
        )
