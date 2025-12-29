from pathlib import Path
import uuid
import shutil

TEMP_DIR = Path("tmp_uploads")
TEMP_DIR.mkdir(exist_ok=True)

def save_temp_file(upload_file)-> Path:
    """
    Save uploaded file temporarily and return file path.

    """
    suffix = Path(upload_file.filename).suffix # Take the uploaded filename and extract just its extension. like agar user dipak.txt upload karega and uska naam change karna hai par .txt ko hum extract kar rahe hai and suffix me rakh rahe hai.
  
    temp_filename= f"{uuid.uuid4().hex}{suffix}" # Here a unique file name is generated with same suffix like .txt or .png 

    temp_path = TEMP_DIR / temp_filename

        # Yaha pe hum uploaded file ko save kar rahe hain.
        # User jo file upload karta hai, usko hum ek temp path par store karte hain.
        # Fir us file ko "wb" (write + binary) mode me open karte hain.
        # shutil.copyfileobj(upload_file.file, buffer) file ko chunks me likhta hai,
        # isse memory par zyada load nahi padta. 
         
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file,buffer)

    return temp_path

def cleanup_temp_file(path: Path):
    if(path.exists()):
        path.unlink()









