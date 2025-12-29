import re
from typing import Dict, List
import tiktoken
import hashlib

#PAGE_PATTERN =  re.compile(r"\[\PAGE (\d+)\]") # Too Rigid Regex Pattern
PAGE_PATTERN = re.compile(r"\[\s*PAGE\s+(\d+)\s*\]", re.IGNORECASE)


############################### Splitting text into pages ###########################
def split_by_page(text:str) -> Dict[int, str]:
    """
    Split text into pages using [PAGE X] markers.
    Returns {page_number: page_text}
    """
     # Yeh function text ko pages me todta hai
    # Aur assume karta hai ke har page ka marker aisa hota hai: [PAGE 1], [PAGE 2], ...
    # Output: ek dictionary {page_number: page_text}

    pages = {}          # yahan hum final result store karenge -> page_number : content
    buffer = []         # current page ke lines temporarily store karne ke liye
    current_page = None # abhi hum kaunse page par hain (start me none)

    for line in text.splitlines(): # text ko line-by-line padho

        match = PAGE_PATTERN.match(line.strip()) # check karo: kya yeh line [PAGE X] hai?

        if match: # Agar yeh ek naya page marker hai

            if current_page is not None:
                # Agar pehle se koi page chal raha tha,
                # to us page ka content save kar do dictionary me

                pages[current_page] = "\n".join(buffer).strip()

                # next page ke liye buffer ko reset karo

                buffer = []

                # Ab new page start ho gaya.
                # Regex se page number nikaalo: match.group(1) -> "5" like string

                current_page = int(match.group(1))
        else:

            # Agar line page marker nahi hai,
            # simply usko current page ke content (buffer) me add kar do

            buffer.append(line)

        # Loop khatam hone ke baad LAST page bhi save karna zaroori hai
        # warna last page ka content dictionary me nahi jayega
    if current_page is not None:
        pages[current_page] = "\n".join(buffer).strip()

    if not pages:
        pages[1] = text.strip()  # Agar koi page markers nahi mile, to pura text ek hi page maan lo

    ############## a dictionary return karo jisme page_number: page_text ho ########################
    return pages 



############################## Makes Chunks of text in a single page ###########################

def chunk_page_text(
        page_text:str,
        page_number:int,
        chunk_size:int = 600,
        overlap:int = 150,
)->List[Dict]:
    """
    Chunk a single page into token-aware chunks.
    Returns list of chunk dicts with metadata.
    """
    enc =  tiktoken.get_encoding("cl100k_base") # this tell tiktoken kaunsa encoding use kare
    tokens = enc.encode(page_text) # text ko tokens me convert karo

    chunks = []
    start = 0
    chunk_index = 0

    # Yahan hum text ko token-based chunks me tod rahe hain.
# Har chunk approx `chunk_size` (e.g., 600) tokens ka hota hai,
# lekin LAST chunk chhota ho sakta hai agar tokens kam bach gaye.
# `overlap` ki wajah se kuch tokens next chunk me repeat hote hain,
# taaki context cut na ho (sentences break na ho).


    while start < len(tokens):
        end = start +chunk_size # so if start= 200  end  =  600+ 200=800 

        chunk_tokens = tokens[start:end] # tokens ka slice le lo from start to end

        chunk_text = enc.decode(chunk_tokens) # tokens ko wapas text me convert karo 
 
        # Chunk metadata ke sath ek dict banao aur usko chunks list me add karo
        
        ########################## Yahi Return value hoga function ka###########
        
        chunks.append({
            "page": page_number,
            "chunk_index": chunk_index,
            "text": chunk_text.strip(),
            "token_count": len(chunk_tokens),
        })

        start +=chunk_size -overlap
        chunk_index +=1

    return chunks




############################## Makes Chunks of text in a full document ###########################

def chunk_document(
        preprocessd_text:str,
        chunk_size:int=600,
        overlap:int=150
)->List[Dict]:
  """
    Split full document into page-aware chunks.
    """
  pages = split_by_page(preprocessd_text)
  all_chunks = []

  for page_number , page_text in pages.items():
      if not page_text.strip():
          continue
      
      page_chunks= chunk_page_text(
          page_text = page_text,
            page_number= page_number,
            chunk_size= chunk_size,
            overlap= overlap,
      )
      all_chunks.extend(page_chunks) # extend se hum ek list me dusri list ke sare elements add kar sakte hain

  return all_chunks # return all chunks from all pages in a single list
  


############################## Generate Unique Chunk ID ###########################

def generate_chunk_id(
        filename:str,
        page:int,
        chunk_index:int
)->str :
    # filename + page + chunk_index ko combine karke
# deterministic (repeatable) unique ID bana rahe hain.
# SHA-256 use karne se: same chunk -> same ID, aur collisions bohot rare hote hain.

    raw = f"{filename}: {page}: {chunk_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()




############################## Build Final Chunks with Metadata ###########################

# Yeh function pura document leta hai aur uske chunks banata hai
# Har chunk me unique ID aur metadata hota hai  
# Returns list of final chunk dicts ready for storage.
# Final call Function. 

def build_chunks(
        filename:str,
        prerocessd_text:str,
)-> List[Dict]:
    chunks  = chunk_document(prerocessd_text) # pura document chunks me tod do and chunks is a list of dicts

    final_chunks = []

    for ch in chunks:
        final_chunks.append({
            "id": generate_chunk_id(
                filename= filename,
                page= ch["page"],
                chunk_index= ch["chunk_index"]
            ),
            "text": ch["text"],
            "metadata":{
                "filename": filename,
                "page": ch["page"],
                "chunk_index": ch["chunk_index"],
                "token_count": ch["token_count"],
                "source":"text",
            },
            
        })

    return final_chunks



