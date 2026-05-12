from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class Cluster:
    cluster_id: str
    signal_ids: List[str]
    size: int

    dominant_risk_topic: Optional[str]
    stores: List[str]
    systems: List[str]

    keywords: List[str]
    summary: Optional[str]

    risk_score: float
    meta: Dict[str, Any]

    # Enrichissement business
    business_title: Optional[str] = None
    executive_summary: Optional[str] = None
    recommended_action: Optional[str] = None
    confidence_level: Optional[str] = None  # e.g. "low" / "medium" / "high"
