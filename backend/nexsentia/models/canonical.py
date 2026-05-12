from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class CanonicalSignal:
    signal_id: str
    source_system: str
    source_object_type: str
    source_object_id: str
    event_timestamp: datetime

    title: str
    body: str
    body_raw: str
    body_clean: str
    body_latest_message: str
    body_history: str

    language: str
    participants: List[str]
    thread_id: Optional[str]

    store: Optional[str]
    risk_topic: Optional[str]
    systems_mentioned: List[str]

    privacy_flag: str
    anonymization_status: str

    raw_metadata: Dict[str, Any]
