import os
import pickle
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer

VOCAB_PATH = "app/embeddings/sparse/vocabulary.pkl"

class TfidfSparseEncoder:
    def __init__(self):
        self.vectorizer = None

        if os.path.exists(VOCAB_PATH):
            with open(VOCAB_PATH, "rb") as f:
                self.vectorizer = pickle.load(f)

    def is_fitted(self) -> bool:
        return self.vectorizer is not None

    def fit(self, texts: List[str]):
        if self.is_fitted():
            raise RuntimeError("TF-IDF vocabulary already exists")

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            max_features=20000,
            ngram_range=(1, 2),
        )

        self.vectorizer.fit(texts)

        os.makedirs(os.path.dirname(VOCAB_PATH), exist_ok=True)
        with open(VOCAB_PATH, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def encode(self, text: str):
        if not self.is_fitted():
            raise RuntimeError("TF-IDF vocabulary not initialized")

        vec = self.vectorizer.transform([text]).tocoo()

        return {
            "indices": vec.col.tolist(),
            "values": vec.data.tolist(),
        }
