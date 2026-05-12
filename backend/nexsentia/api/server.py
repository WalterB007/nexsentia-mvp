import json
import os
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from ..api.models import ClusterOut, SignalOut

app = FastAPI(
    title="Nexsentia MVP API",
    version="0.1.0",
)

# CORS très ouvert pour MVP / local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_clusters_enriched() -> List[Dict[str, Any]]:
    base_dir = os.path.abspath("../data/vectors")
    path = os.path.join(base_dir, "clusters_enriched.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_signals_raw() -> List[Dict[str, Any]]:
    base_dir = os.path.abspath("../data/raw")
    path = os.path.join(base_dir, "signals.jsonl")
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}


@app.get("/clusters/top", response_model=List[ClusterOut], tags=["clusters"])
async def get_top_clusters(limit: int = Query(5, ge=1, le=50)):
    clusters_raw = _load_clusters_enriched()
    if not clusters_raw:
        return []

    clusters_raw.sort(key=lambda c: c.get("risk_score", 0.0), reverse=True)
    clusters_raw = clusters_raw[:limit]

    clusters_out = [
        ClusterOut(
            cluster_id=c["cluster_id"],
            size=c["size"],
            dominant_risk_topic=c.get("dominant_risk_topic"),
            stores=c.get("stores", []),
            systems=c.get("systems", []),
            keywords=c.get("keywords", []),
            risk_score=c.get("risk_score", 0.0),
            business_title=c.get("business_title"),
            executive_summary=c.get("executive_summary"),
            recommended_action=c.get("recommended_action"),
            confidence_level=c.get("confidence_level"),
            meta=c.get("meta", {}),
        )
        for c in clusters_raw
    ]
    return clusters_out


@app.get("/clusters/{cluster_id}", response_model=ClusterOut, tags=["clusters"])
async def get_cluster(cluster_id: str):
    clusters_raw = _load_clusters_enriched()
    for c in clusters_raw:
        if c.get("cluster_id") == cluster_id:
            return ClusterOut(
                cluster_id=c["cluster_id"],
                size=c["size"],
                dominant_risk_topic=c.get("dominant_risk_topic"),
                stores=c.get("stores", []),
                systems=c.get("systems", []),
                keywords=c.get("keywords", []),
                risk_score=c.get("risk_score", 0.0),
                business_title=c.get("business_title"),
                executive_summary=c.get("executive_summary"),
                recommended_action=c.get("recommended_action"),
                confidence_level=c.get("confidence_level"),
                meta=c.get("meta", {}),
            )
    raise HTTPException(status_code=404, detail="Cluster not found")


@app.get("/signals", response_model=List[SignalOut], tags=["signals"])
async def get_signals(cluster_id: Optional[str] = None, limit: int = Query(50, ge=1, le=200)):
    signals_raw = _load_signals_raw()
    if not signals_raw:
        return []

    cluster_ids_by_signal: Dict[str, List[str]] = {}
    clusters_raw = _load_clusters_enriched()
    for c in clusters_raw:
        cid = c.get("cluster_id")
        for sid in c.get("signal_ids", []):
            cluster_ids_by_signal.setdefault(sid, []).append(cid)

    out: List[SignalOut] = []
    for row in signals_raw:
        sid = row["signal_id"]
        if cluster_id:
            if cluster_id not in cluster_ids_by_signal.get(sid, []):
                continue

        ts = row.get("event_timestamp")
        if isinstance(ts, str):
            try:
                parsed = datetime.fromisoformat(ts)
                ts_out = parsed.isoformat()
            except Exception:
                ts_out = ts
        else:
            ts_out = None

        out.append(
            SignalOut(
                signal_id=sid,
                source_system=row.get("source_system", ""),
                source_object_type=row.get("source_object_type", ""),
                source_object_id=row.get("source_object_id", ""),
                title=row.get("title", ""),
                body_latest_message=row.get("body_latest_message", "") or row.get("body", ""),
                store=row.get("store"),
                risk_topic=row.get("risk_topic"),
                systems_mentioned=row.get("systems_mentioned", []),
                event_timestamp=ts_out,
            )
        )

        if len(out) >= limit:
            break

    return out

@app.post("/pipeline/run", tags=["pipeline"])
async def run_pipeline():
    project_root = os.path.abspath("..")
    backend_dir = os.path.join(project_root, "backend")
    venv_python = os.path.join(project_root, "venv", "bin", "python")

    commands = [
        [venv_python, "-m", "nexsentia.scripts.ingest_outlook"],
        [venv_python, "-m", "nexsentia.scripts.embed_signals"],
        [venv_python, "-m", "nexsentia.scripts.build_clusters"],
        [venv_python, "-m", "nexsentia.scripts.enrich_clusters"],
    ]

    results = []

    for cmd in commands:
        proc = subprocess.run(
            cmd,
            cwd=backend_dir,
            capture_output=True,
            text=True,
        )

        if proc.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "step": " ".join(cmd),
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                },
            )

        results.append(
            {
                "step": " ".join(cmd),
                "stdout": proc.stdout,
            }
        )

    return {
        "status": "ok",
        "steps": results,
    }
