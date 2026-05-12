from collections import Counter, defaultdict
from typing import List, Dict, Tuple

import numpy as np
import umap
import hdbscan

from ..models.canonical import CanonicalSignal
from ..models.clustering import Cluster
from ..risk.scoring import compute_risk_score


def umap_hdbscan_clustering(
    embeddings: np.ndarray,
    min_cluster_size: int = 5,
    min_samples: int = 2,
    random_state: int = 42,
) -> np.ndarray:
    """
    Applique UMAP puis HDBSCAN et retourne un label pour chaque vecteur.
    Les labels -1 sont considérés comme bruit.
    """
    if embeddings.shape[0] == 0:
        return np.array([])

    reducer = umap.UMAP(
        n_neighbors=10,
        n_components=10,
        metric="cosine",
        random_state=random_state,
    )

    reduced = reducer.fit_transform(embeddings)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="euclidean",
        cluster_selection_method="eom",
    )

    labels = clusterer.fit_predict(reduced)
    return labels


def build_clusters(
    signals: List[CanonicalSignal],
    embeddings: np.ndarray,
    ids: List[str],
) -> List[Cluster]:
    """
    Construit des objets Cluster à partir des signaux, embeddings et ids.
    """
    if not signals or embeddings.shape[0] == 0:
        return []

    id_to_signal: Dict[str, CanonicalSignal] = {s.signal_id: s for s in signals}
    labels = umap_hdbscan_clustering(embeddings)

    if labels.size == 0:
        return []

    clusters_by_label: Dict[int, List[str]] = defaultdict(list)
    for idx, label in enumerate(labels):
        if label == -1:
            continue  # bruit pour l'instant
        clusters_by_label[label].append(ids[idx])

    clusters: List[Cluster] = []

    for label, sig_ids in clusters_by_label.items():
        cluster_signals = [id_to_signal[sid] for sid in sig_ids if sid in id_to_signal]

        size = len(cluster_signals)
        if size == 0:
            continue

        topics = [s.risk_topic for s in cluster_signals if s.risk_topic]
        stores = [s.store for s in cluster_signals if s.store]
        systems = [sys for s in cluster_signals for sys in s.systems_mentioned]

        dominant_topic = None
        if topics:
            dominant_topic = Counter(topics).most_common(1)[0][0]

        # keywords simples : top mots fréquents du titre + body_latest_message
        text_blob = " ".join(
            (s.title + " " + (s.body_latest_message or s.body or ""))
            for s in cluster_signals
        ).lower()

        tokens = [
            t.strip(".,;:!?()[]\"'") for t in text_blob.split()
            if len(t) > 3
        ]

        stopwords = {
            "this", "that", "with", "from", "have", "been", "will",
            "into", "about", "your", "ours", "them", "they",
            "super", "150s", "rome", "milan", "flagship", "store",
            "delay", "delays", "shipments", "shipment",
        }

        tokens = [t for t in tokens if t not in stopwords]
        most_common = [w for w, _ in Counter(tokens).most_common(8)]

        risk_score = compute_risk_score(cluster_signals)

        cluster = Cluster(
            cluster_id=f"cluster_{label}",
            signal_ids=sig_ids,
            size=size,
            dominant_risk_topic=dominant_topic,
            stores=sorted(set(stores)),
            systems=sorted(set(systems)),
            keywords=most_common,
            summary=None,
            risk_score=risk_score,
            meta={
                "raw_label": int(label),
            },
        )
        clusters.append(cluster)

    return clusters
