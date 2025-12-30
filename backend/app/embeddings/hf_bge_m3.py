#### Original code (commented as requested)
# import os
# import requests
# from typing import List
# from app.embeddings.base import EmbeddingModel
# from app.config import settings
#
# ############## IMPORTING CONFIG VARIABLES ##############
# HF_API_TOKEN = settings.HF_API_TOKEN
# HF_EMBEDDING_MODEL = settings.HF_EMBEDDING_MODEL
# HF_API_URL_BGE = settings.HF_API_URL_BGE
#
# # Default to the feature-extraction endpoint for bge-m3 if the env var is missing.
# DEFAULT_API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-m3/feature-extraction"
# API_URL = HF_API_URL_BGE or DEFAULT_API_URL
#
# HEADERS = {
#    "Authorization": f"Bearer {HF_API_TOKEN}",
# }
#
#
# class HFBgeM3Embedder(EmbeddingModel):
#    def _call(self, inputs):
#       # HF feature-extraction accepts a single string or a list of strings.
#       payload = {
#          "inputs": inputs,
#          "options": {"wait_for_model": True},
#       }
#
#       resp = requests.post(
#          API_URL,
#          headers=HEADERS,
#          json=payload,
#          timeout=60,
#       )
#
#       if not resp.ok:
#          raise requests.HTTPError(
#             f"HF inference request failed ({resp.status_code}): {resp.text}",
#             response=resp,
#          )
#
#       return resp.json()
#
#    def embed_documents(self, texts: List[str]) -> List[List[float]]:
#       outputs = self._call(texts)  # HF returns List[List[float]] for feature-extraction
#       return self._normalize(outputs)
#
#    def embed_query(self, text: str) -> List[float]:
#       vec = self._call(text)
#       vec = vec[0] if isinstance(vec, list) else vec
#       return self._normalize([vec])[0]
#
#    def dimensions(self) -> int:
#       # bge-m3 is 1024 dimensional
#       return 1024
#
#    @staticmethod
#    def _normalize(vectors: List[List[float]]) -> List[List[float]]:
#       import math
#
#       normed = []
#       for v in vectors:
#          s = math.sqrt(sum(x * x for x in v)) or 1.0
#          normed.append([x / s for x in v])
#       return normed


#### New code (active)
import os
import requests
from typing import List
from app.embeddings.base import EmbeddingModel
from app.config import settings

HF_API_TOKEN = settings.HF_API_TOKEN
HF_API_URL_BGE = settings.HF_API_URL_BGE

# Default to the feature-extraction endpoint for bge-m3 if the env var is missing.
DEFAULT_API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-m3/feature-extraction"
API_URL = HF_API_URL_BGE or DEFAULT_API_URL
# Some configs may accidentally point to the sentence-similarity pipeline; force feature-extraction.
if "sentence-similarity" in API_URL:
    API_URL = API_URL.replace("sentence-similarity", "feature-extraction")

HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


class HFBgeM3Embedder(EmbeddingModel):
    def _call(self, inputs):
        payload = {
            "inputs": inputs,  # accepts str or List[str]
            "options": {"wait_for_model": True},
        }

        resp = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=60,
        )

        # Raise with body for easier debugging
        if not resp.ok:
            raise requests.HTTPError(
                f"HF inference request failed ({resp.status_code}): {resp.text}",
                response=resp,
            )

        return resp.json()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        outputs = self._call(texts)
        return self._normalize(outputs)

    def embed_query(self, text: str) -> List[float]:
        vec = self._call(text)
        vec = vec[0] if isinstance(vec, list) else vec
        return self._normalize([vec])[0]

    def dimension(self) -> int:
        # bge-m3 is 1024 dimensional
        return 1024

    @staticmethod
    def _normalize(vectors: List[List[float]]) -> List[List[float]]:
        import math

        normed = []
        for v in vectors:
            s = math.sqrt(sum(x * x for x in v)) or 1.0
            normed.append([x / s for x in v])
        return normed

