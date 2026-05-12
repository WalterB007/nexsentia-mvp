from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ClusterOut(BaseModel):
    cluster_id: str
    size: int
    dominant_risk_topic: Optional[str]
    stores: List[str]
    systems: List[str]
    keywords: List[str]

    risk_score: float
    business_title: Optional[str]
    executive_summary: Optional[str]
    recommended_action: Optional[str]
    confidence_level: Optional[str]

    meta: Dict[str, Any]


class SignalOut(BaseModel):
    signal_id: str
    source_system: str
    source_object_type: str
    source_object_id: str

    title: str
    body_latest_message: str
    store: Optional[str]
    risk_topic: Optional[str]
    systems_mentioned: List[str]

    event_timestamp: Optional[str]
