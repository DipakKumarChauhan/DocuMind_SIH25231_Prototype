"""
Local BGE-m3 embedding model implementation using sentence-transformers.
This module provides a local alternative to HuggingFace API-based embeddings.
"""

import os
import math
from typing import List
from sentence_transformers import SentenceTransformer
from app.embeddings.base import EmbeddingModel


class LocalBgeM3Embedder(EmbeddingModel):
    """
    Local BGE-m3 embedder using sentence-transformers.
    
    BGE-m3 is a multilingual embedding model that supports:
    - Dense embeddings (1024 dimensions)
    - Sparse BM25 embeddings
    - Multi-lingual support (100+ languages)
    
    This implementation uses dense embeddings by default.
    """
    
    # Model name from Hugging Face
    MODEL_NAME = "BAAI/bge-m3"
    
    # Embedding dimension for BGE-m3
    EMBEDDING_DIM = 1024
    
    def __init__(self, cache_folder: str = None, device: str = "cpu"):
        """
        Initialize the local BGE-m3 embedder.
        
        Args:
            cache_folder: Optional folder to cache model weights. 
                         Defaults to ~/.cache/huggingface/hub/
            device: Device to run model on ("cpu", "cuda", "mps", etc.)
        """
        self.device = device
        self.cache_folder = cache_folder or os.path.expanduser("~/.cache/huggingface/hub/")
        
        # Load the model
        try:
            self.model = SentenceTransformer(
                self.MODEL_NAME,
                cache_folder=self.cache_folder,
                device=device,
                trust_remote_code=True
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to load BGE-m3 model from {self.MODEL_NAME}. "
                f"Error: {str(e)}. Make sure transformers and sentence-transformers are installed."
            )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of normalized embedding vectors (each 1024-dimensional)
        """
        if not texts:
            return []
        
        # Generate embeddings (already normalized by sentence-transformers)
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False
        )
        
        # Convert to list of lists if needed
        return [emb.tolist() if hasattr(emb, 'tolist') else emb for emb in embeddings]
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            text: Query text string
            
        Returns:
            Normalized embedding vector (1024-dimensional)
        """
        if not text:
            return [0.0] * self.EMBEDDING_DIM
        
        # Generate embedding (already normalized by sentence-transformers)
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        # Convert to list if needed
        return embedding.tolist() if hasattr(embedding, 'tolist') else embedding
    
    def dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            Embedding dimension (1024 for BGE-m3)
        """
        return self.EMBEDDING_DIM
    
    @staticmethod
    def _normalize(vectors: List[List[float]]) -> List[List[float]]:
        """
        Normalize vectors to unit length (L2 normalization).
        
        Args:
            vectors: List of embedding vectors
            
        Returns:
            List of normalized vectors
        """
        normed = []
        for v in vectors:
            if isinstance(v, (list, tuple)):
                # Calculate L2 norm (magnitude)
                norm = math.sqrt(sum(x * x for x in v)) or 1.0
                # Normalize by dividing by magnitude
                normed.append([x / norm for x in v])
            else:
                # Fallback for invalid input
                normed.append([1.0] * 1024)
        
        return normed


# Singleton instance for efficiency (optional, can be created per request)
_embedder_instance = None


def get_local_bge_m3_embedder(
    cache_folder: str = None,
    device: str = "cpu"
) -> LocalBgeM3Embedder:
    """
    Get or create a local BGE-m3 embedder instance.
    
    Args:
        cache_folder: Optional folder to cache model weights
        device: Device to run model on
        
    Returns:
        LocalBgeM3Embedder instance
    """
    global _embedder_instance
    
    if _embedder_instance is None:
        _embedder_instance = LocalBgeM3Embedder(
            cache_folder=cache_folder,
            device=device
        )
    
    return _embedder_instance
