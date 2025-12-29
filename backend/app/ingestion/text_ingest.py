from pathlib import Path
import fitz  # PyMuPDF
import docx

def extract_raw_text(file_path:Path)->str:

    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(file_path)
    elif suffix == ".docx":
        return _extract_docx(file_path)
    # elif suffix in [".txt"]:
    #     return _extract_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
    

def _extract_pdf(path:Path)-> str:
    text=[]
    doc = fitz.open(path)
    
    for page_number , page in enumerate(doc,start=1):
        page_text = page.get_text()
        if page_text.strip():
            text.append(f"[PAGE {page_number}]\n{page_text}")
        
    return "\n".join(text)

def _extract_docx(path:Path)->str:
   
   doc = docx.Document(path)
   paragraphs= []
   
   for para in doc.paragraphs:
       if para.text.strip():
            paragraphs.append(para.text)
    
   return "\n".join(paragraphs)