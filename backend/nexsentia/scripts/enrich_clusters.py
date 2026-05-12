import json
import os
from dataclasses import asdict
from typing import List

from ..models.clustering import Cluster
from ..nlp.cluster_enrichment import enrich_clusters_business


def load_clusters(path: str) -> List[Cluster]:
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    clusters: List[Cluster] = []
    for row in raw:
        c = Cluster(
            cluster_id=row["cluster_id"],
            signal_ids=row["signal_ids"],
            size=row["size"],
            dominant_risk_topic=row.get("dominant_risk_topic"),
            stores=row.get("stores", []),
            systems=row.get("systems", []),
            keywords=row.get("keywords", []),
            summary=row.get("summary"),
            risk_score=row.get("risk_score", 0.0),
            meta=row.get("meta", {}),
            business_title=row.get("business_title"),
            executive_summary=row.get("executive_summary"),
            recommended_action=row.get("recommended_action"),
            confidence_level=row.get("confidence_level"),
        )
        clusters.append(c)

    return clusters


def run_enrich_clusters():
    base_dir = os.path.abspath("../data/vectors")
    clusters_path = os.path.join(base_dir, "clusters.json")
    out_path = os.path.join(base_dir, "clusters_enriched.json")

    clusters = load_clusters(clusters_path)
    if not clusters:
        print("[WARN] No clusters found to enrich.")
        return

    print(f"[INFO] Loaded {len(clusters)} clusters.")
    clusters = enrich_clusters_business(clusters)

    for c in clusters:
        print("----")
        print(f"{c.cluster_id} | topic={c.dominant_risk_topic} | risk_score={c.risk_score}")
        print(f"  title: {c.business_title}")
        print(f"  summary: {c.executive_summary}")
        print(f"  action: {c.recommended_action}")
        print(f"  confidence: {c.confidence_level}")

    serializable = [asdict(c) for c in clusters]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Enriched clusters saved to {out_path}")


if __name__ == "__main__":
    run_enrich_clusters()
