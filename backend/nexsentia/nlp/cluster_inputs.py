import json
import os
from typing import List, Tuple

import numpy as np

from ..models.canonical import CanonicalSignal


def load_signals(path: str) -> List[CanonicalSignal]:
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
        sig = CanonicalSignal(
            signal_id=row["signal_id"],
            source_system=row["source_system"],
            source_object_type=row["source_object_type"],
            source_object_id=row["source_object_id"],
            event_timestamp=None,  # pas utilisé ici

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


def load_embeddings_and_ids(base_dir: str = "../data/vectors") -> Tuple[np.ndarray, list]:
    embeddings_path = os.path.abspath(os.path.join(base_dir, "embeddings.npy"))
    index_path = os.path.abspath(os.path.join(base_dir, "index.json"))

    if not (os.path.exists(embeddings_path) and os.path.exists(index_path)):
        return np.zeros((0, 0)), []

    embs = np.load(embeddings_path)
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    ids = [item["id"] for item in index]
    return embs, ids
