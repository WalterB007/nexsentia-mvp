from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    @property
    def dim(self) -> int:
        # Encode a small dummy sentence to infer dimension
        emb = self._model.encode(["test"], normalize_embeddings=True)
        return int(emb.shape[1])

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Retourne un array (n, d) de vecteurs normalisés.
        """
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings
