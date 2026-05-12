import json
import os
from typing import List, Tuple, Dict
import numpy as np


class LocalNumpyVectorStore:
    """
    Vector store local basé sur un fichier .npy et un index JSON.
    dim : dimension des embeddings
    """

    def __init__(self, base_dir: str = "../data/vectors", dim: int = 384):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
        self.dim = dim
        self.vectors_path = os.path.join(self.base_dir, "embeddings.npy")
        self.index_path = os.path.join(self.base_dir, "index.json")
        self._embeddings = None  # type: ignore
        self._index = []  # type: ignore

        self._load()

    def _load(self):
        if os.path.exists(self.vectors_path):
            self._embeddings = np.load(self.vectors_path)
        else:
            self._embeddings = np.zeros((0, self.dim), dtype="float32")

        if os.path.exists(self.index_path):
            with open(self.index_path, "r", encoding="utf-8") as f:
                self._index = json.load(f)
        else:
            self._index = []

    def _save(self):
        np.save(self.vectors_path, self._embeddings)
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(self._index, f, ensure_ascii=False, indent=2)

    @property
    def size(self) -> int:
        return int(self._embeddings.shape[0])

    def add(self, ids: List[str], vectors: np.ndarray, payloads: List[Dict]):
        """
        Ajoute de nouveaux vecteurs.
        ids: liste de signal_id
        vectors: array (n, dim) déjà normalisés
        payloads: infos complémentaires (ex: risk_topic, store, etc.)
        """
        if vectors.shape[1] != self.dim:
            raise ValueError(f"Expected dim={self.dim}, got {vectors.shape[1]}")

        # Filtrage des doublons par id
        existing_ids = {item["id"] for item in self._index}
        new_rows = []
        new_payloads = []
        for idx, sig_id in enumerate(ids):
            if sig_id in existing_ids:
                continue
            new_rows.append(vectors[idx])
            new_payloads.append({"id": sig_id, "payload": payloads[idx]})

        if not new_rows:
            return 0

        new_rows_np = np.vstack(new_rows).astype("float32")
        self._embeddings = np.vstack([self._embeddings, new_rows_np])
        self._index.extend(new_payloads)
        self._save()
        return len(new_rows)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        Recherche les top_k plus proches voisins par similarité cosinus.
        Les vecteurs sont supposés normalisés (||v||=1).
        """
        if self.size == 0:
            return []

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        # cos sim = dot product car vecteurs normalisés
        sims = (self._embeddings @ query_vector.T).reshape(-1)
        top_idx = np.argsort(sims)[::-1][:top_k]

        results = []
        for idx in top_idx:
            meta = self._index[idx]
            results.append(
                {
                    "id": meta["id"],
                    "payload": meta["payload"],
                    "score": float(sims[idx]),
                }
            )
        return results
