from typing import List, Dict
from ..models.canonical import CanonicalSignal

CRITICAL_TOPICS = {
    "Order Promise Risk": 1.2,
    "Packaging Shortage": 1.1,
    "Shipping Blockage": 1.1,
    "Manufacturing Quality": 1.05,
}

def compute_risk_score(signals: List[CanonicalSignal]) -> float:
    """
    Risk Score simple:
    - base sur log(volume)
    - + bonus selon le nombre de boutiques et systèmes distincts
    - + multiplicateur sur certains topics critiques
    """

    if not signals:
        return 0.0

    volume = len(signals)
    stores = {s.store for s in signals if s.store}
    systems = {sys for s in signals for sys in s.systems_mentioned}
    topics = {s.risk_topic for s in signals if s.risk_topic}

    import math
    base = math.log10(volume + 1) * 20  # 1 → ~6, 10 → ~20

    bonus_stores = len(stores) * 3.0
    bonus_systems = len(systems) * 1.5

    multiplier = 1.0
    for t in topics:
        if t in CRITICAL_TOPICS:
            multiplier *= CRITICAL_TOPICS[t]

    score = (base + bonus_stores + bonus_systems) * multiplier

    return round(score, 2)
