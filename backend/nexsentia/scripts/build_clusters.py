import json
import os
from dataclasses import asdict
from typing import List

from ..nlp.cluster_inputs import load_signals, load_embeddings_and_ids
from ..nlp.clustering import build_clusters
from ..models.clustering import Cluster


def run_build_clusters():
    signals_path = os.path.abspath("../data/raw/signals.jsonl")
    vectors_dir = os.path.abspath("../data/vectors")

    signals = load_signals(signals_path)
    embeddings, ids = load_embeddings_and_ids(vectors_dir)

    print(f"[INFO] Loaded {len(signals)} signals, {embeddings.shape[0]} embeddings.")

    # filtrer les signaux qui ont des embeddings
    id_set = set(ids)
    signals = [s for s in signals if s.signal_id in id_set]

    clusters: List[Cluster] = build_clusters(signals, embeddings, ids)

    print(f"[INFO] Built {len(clusters)} clusters.")
    for c in clusters:
        print("----")
        print(f"{c.cluster_id} | size={c.size} | risk_score={c.risk_score}")
        print(f"  topic={c.dominant_risk_topic}")
        print(f"  stores={c.stores}")
        print(f"  systems={c.systems}")
        print(f"  keywords={c.keywords}")

    output_path = os.path.abspath("../data/vectors/clusters.json")
    serializable = [asdict(c) for c in clusters]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Clusters saved to {output_path}")


if __name__ == "__main__":
    run_build_clusters()
