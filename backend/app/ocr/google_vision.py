from google.cloud import vision

from typing import List, Dict

client = vision.ImageAnnotatorClient()

def extract_text_from_image(image_url: str) -> List[Dict]:
    """
    Returns list of OCR blocks with text + bounding boxes
    """
    image = vision.Image() # creates an empty Vision API image container
    image.source.image_uri = image_url # Is URL wali image Vision API ko detect/analyze karne ke liye de rahe hain

    response =  client.text_detection(image=image)

    if response.error.message:
        raise RuntimeError(response.error.message)
    
    results = []

    # Skip full-page annotation (index 0)

    # Loop through each detected text item (skip index 0 because it is the full combined text)

    for annotations in response.text_annotations[1:]:

          # Collect the coordinates of the bounding box around the text

        vertices = [
            {"x": v.x, "y": v.y} # store x and y for each corner point
            for v in annotations.bounding_poly.vertices
        ]

        # Add the detected text and its bounding box to the results list

        results.append({
            "text": annotations.description, # actual text detected
            "bounding_box": vertices  # location of the text in the image
        })
    return results






