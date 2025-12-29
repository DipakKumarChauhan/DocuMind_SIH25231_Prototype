import re
from typing import List

################### Preprocessing functions/methods Utilities ###################
def basic_clean(text:str)->str:
   """
    Safe text cleanup:
    - remove null chars
    - normalize whitespace
    - preserve page markers
    """
   
   # Remove null characters
   text =  text.replace("\x00","")

   # normalize line endings
   text = text.replace('\r\n', "\n").replace("\r","\n")

   # Remove  excessive  blank  (keep max 2)
   text = re.sub(r"\n{3,}","\n\n",text)

   # Strip trailling spaces
   text = "\n".join(line.rstrip() for line in text.splitlines())

   return text.strip()

def remove_headers_footers(text:str, min_repeats: int = 3)->str:
   """
    Remove repeating header/footer lines based on frequency.
    Page markers are preserved.
    """
   lines = text.splitlines()

   line_freq = {}
   
   for line in lines:
      clean_line = line.strip()
      if clean_line and not clean_line.startswith("[Page"):
         line_freq[clean_line] = line_freq.get(clean_line,0)+1
    
    
   filtered_lines = []
   for line in lines:
      stripped = line.strip()

      if stripped.startswith("[Page"):
        filtered_lines.append(line)
        continue
      
      if line_freq.get(stripped,0) >= min_repeats and  len(stripped) < 80:
        continue
      
      filtered_lines.append(line)
      
   return "\n".join(filtered_lines)
        

def normalize_withespace(text:str) -> str:
       
    """
    Normalize spacing without altering structure.
    """

    #collapse spaces /tabs
    text = re.sub(r"[\t]+", " ", text)

    # Ensure page markers are seperated
    text = re.sub(r"(\[PAGE \d+\]])", r"\n\1\n",text)

    # clean up again
    text = re.sub(r"\n{3,}", "\n\n" , text)

    return text.strip()



############################# Main Function That calls above methods #############################
def preprocess_text(raw_text: str)->str:
   text =  basic_clean(raw_text)
   text = remove_headers_footers(text)
   text = normalize_withespace(text)
   return text
    

        
      