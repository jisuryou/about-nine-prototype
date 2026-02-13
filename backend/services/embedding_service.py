import os
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: Optional[str] = None):
        self._model_name = model_name or os.getenv(
            "SENTENCE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self._model = None

    def _load(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def encode_text(self, text: str) -> Optional[List[float]]:
        if not text or not text.strip():
            return None
        try:
            model = self._load()
            vec = model.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            return vec.astype(float).tolist()
        except Exception:
            return None


def normalize_vector(vec: List[float]) -> List[float]:
    if not vec:
        return vec
    arr = np.array(vec, dtype=float)
    norm = np.linalg.norm(arr)
    if norm == 0:
        return arr.tolist()
    return (arr / norm).tolist()
