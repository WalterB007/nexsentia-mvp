from ..models.canonical import CanonicalSignal
from .enrichers import enrich_signal


def process_signal(signal: CanonicalSignal) -> CanonicalSignal:
    return enrich_signal(signal)
