from uuid import uuid4
from typing import List
from app.ocr.google_vision import extract_text_from_image

def build_ocr_chunks(
        image_url:str,
        owner_id:str,
        filename:str,
)-> List[dict]:
    """
    Given an image URL, extract text using OCR and build chunks with metadata
    """
    ocr_results = extract_text_from_image(image_url)

    chunks = []
    for i, block in enumerate(ocr_results):
        if len(block["text"]) < 5:
            continue

        chunks.append({
           "id": str(uuid4()),
            "text": block["text"],
            "metadata" : {
                "owner_id":owner_id,
                "source":"image_ocr",
                "filename":filename,
                "image_url" : image_url,
                "bbox": block["bounding_box"],
                "chunk_index":i,
            }
       })

    return chunks