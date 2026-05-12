import json
import os
from typing import List

import numpy as np

from ..models.canonical import CanonicalSignal
from ..nlp.embeddings import EmbeddingModel
from ..vectorstore.local_numpy_store import LocalNumpyVectorStore


def load_signals_from_jsonl(path: str) -> List[CanonicalSignal]:
    if not os.path.exists(path):
        return []

    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    signals: List[CanonicalSignal] = []
    for row in rows:
        # Attention: on ne reconstruit pas tous les champs datetime,
        # pour l'instant ce n'est pas nécessaire pour les embeddings.
        sig = CanonicalSignal(
            signal_id=row["signal_id"],
            source_system=row["source_system"],
            source_object_type=row["source_object_type"],
            source_object_id=row["source_object_id"],
            event_timestamp=None,  # non utilisé ici

            title=row.get("title", ""),
            body=row.get("body", ""),
            body_raw=row.get("body_raw", ""),
            body_clean=row.get("body_clean", ""),
            body_latest_message=row.get("body_latest_message", ""),
            body_history=row.get("body_history", ""),

            language=row.get("language", "en"),
            participants=row.get("participants", []),
            thread_id=row.get("thread_id"),

            store=row.get("store"),
            risk_topic=row.get("risk_topic"),
            systems_mentioned=row.get("systems_mentioned", []),

            privacy_flag=row.get("privacy_flag", "anonymized"),
            anonymization_status=row.get("anonymization_status", "anonymized"),

            raw_metadata=row.get("raw_metadata", {}),
        )
        signals.append(sig)

    return signals


def run_embedding():
    data_path = os.path.abspath("../data/raw/signals.jsonl")
    signals = load_signals_from_jsonl(data_path)

    if not signals:
        print("[WARN] No signals found to embed.")
        return

    print(f"[INFO] Loaded {len(signals)} signals.")

    model = EmbeddingModel()
    dim = model.dim
    print(f"[INFO] Embedding model: {model.model_name} (dim={dim})")

    store = LocalNumpyVectorStore(dim=dim)

    texts = [
        (sig.title + "\n\n" + (sig.body_latest_message or sig.body or ""))
        for sig in signals
    ]
    ids = [sig.signal_id for sig in signals]
    payloads = [
        {
            "source_system": sig.source_system,
            "store": sig.store,
            "risk_topic": sig.risk_topic,
            "thread_id": sig.thread_id,
        }
        for sig in signals
    ]

    embeddings = model.encode(texts).astype("float32")
    added = store.add(ids, embeddings, payloads)

    print(f"[INFO] Vectors added: {added}")
    print(f"[INFO] Vector store size: {store.size}")


if __name__ == "__main__":
    run_embedding()
