from fastapi import APIRouter,UploadFile,File,HTTPException,Depends

from pathlib import Path
from app.utils.file_utils import save_temp_file, cleanup_temp_file
from app.ingestion.text_ingest import extract_raw_text


###################### Import Auth Dependencies ######################
from app.auth.dependencies  import get_current_user # New Change
from app.auth.models import User

###################### Import Preprocessing Functions ######################
from app.preprocessing.text_preprocess import preprocess_text
from app.chunking.text_chunker import build_chunks 

########################### Import  HF BGE Embedder ##########################

from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
from app.ingestion.text_indexer import index_text_chunks

embedder = HFBgeM3Embedder()


####################### Debugging Helper Function ######################
# Only un commnet if using for debugging in below calling before return statement.

# import re

# def extract_pages_from_text(text: str):
#     return sorted(set(int(p) for p in re.findall(r"\[PAGE (\d+)\]", text)))


route = APIRouter(prefix='/api',tags=["Admin Upload"])

ALLOWED_EXTENSIONS = {".pdf",".docx",}

@route.post("/upload-admin")
def upload_document(
    file:UploadFile=File(...), 
    current_user: User = Depends(get_current_user) # New Change
    ):

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
        
        ############## Debugging Info ################

        # print("=== PREPROCESSED TEXT START ===")
        # print(preprocessed_text[:1000])
        # print("=== PREPROCESSED TEXT END ===")
        
        chunks = build_chunks(
            filename=file.filename, 
            preprocessed_text=preprocessed_text,

            owner_id = current_user.id ####### New Change ########

            )
        inserted = index_text_chunks(chunks, embedder)
        ############## Debuging Info ################
    #     pages_covered = set()
    #     for ch in chunks:
    #         pages_covered.update(extract_pages_from_text(ch["text"]))

    #     return {
    # "status": "success",
    # "filename": file.filename,
    # "total_chunks": len(chunks),
    # "pages_covered": sorted(pages_covered),
    # "sample_chunk": chunks[22] if chunks else None
    #           }    

        return {
            "status": "success",
            "filename": file.filename,
            "total_chunks": len(chunks),
            "vectors_inserted": inserted,
            "pages_in_chunks": list(
        sorted(set(ch["metadata"]["page"] for ch in chunks))
    ),
            "sample_chunk": chunks[0] if chunks else None,
            #"text_preview": preprocessed_text[:100000]
        }
        
    
    finally:
        if temp_path:
            cleanup_temp_file(temp_path)

    
    


   