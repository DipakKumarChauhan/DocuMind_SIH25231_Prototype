from fastapi import APIRouter,UploadFile,File,HTTPException
from pathlib import Path
from app.utils.file_utils import save_temp_file, cleanup_temp_file
from app.ingestion.text_ingest import extract_raw_text

###################### Import Preprocessing Functions ######################
from app.preprocessing.text_preprocess import preprocess_text



route = APIRouter(prefix='/api',tags=["Admin Upload"])

ALLOWED_EXTENSIONS = {".pdf",".docx",}

@route.post("/upload-admin")
def upload_document(file:UploadFile=File(...)):
    suffix = Path(file.filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400,detail=f"Unsupported file type: {suffix}. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}")
    
    temp_path = None

    try:
        temp_path =  save_temp_file(file)
        raw_text = extract_raw_text(temp_path)

        if not raw_text.strip():
            raise HTTPException(status_code= 400, detail= "No readable text found in document")
        preprocessed_text = preprocess_text(raw_text)
        return {
            "status": "success",
            "filename": file.filename,
            "text_preview": preprocessed_text[:100000]
        }
        
    
    finally:
        if temp_path:
            cleanup_temp_file(temp_path)

    
    


   