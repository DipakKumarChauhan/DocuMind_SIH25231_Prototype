from abc import ABC, abstractmethod
from typing import List

class EmbeddingModel(ABC):
    @abstractmethod
    def embed_documents(self,texts:List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self,text:str)->List[float]:
        pass

    @abstractmethod
    def dimension(self)->int:
        pass

# Ye ek abstract base class hai jo sab embedding models ke liye contract set karta hai.
# Jo bhi model isse inherit karega, usse ye methods implement karne hi padenge.
# Isse code clean, consistent aur easily swappable rehta hai.
