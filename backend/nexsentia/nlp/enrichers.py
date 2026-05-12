from typing import Optional
from ..models.canonical import CanonicalSignal
from .cleaning import clean_email_body

STORES = [
    "Paris Flagship",
    "Lyon Centre",
    "Bordeaux",
    "Marseille",
    "Toulouse",
    "Nantes",
    "Strasbourg",
    "Lille",
    "Nice",
    "Rennes",
]

RISK_KEYWORDS = {
    "Packaging Shortage": ["packaging", "carton", "box", "CartaPack"],
    "Order Promise Risk": ["promise", "lead time", "delay", "fitting", "client promises"],
    "Manufacturing Quality": ["quality", "alteration", "defect", "rework"],
    "Shipping Blockage": ["blocked", "parcel", "shipment", "stuck"],
    "Stock Discrepancy": ["stock", "inventory", "discrepancy", "difference"],
    "POS Instability": ["POS", "Cegid", "till", "cash", "crash"],
    "Supply Delay": ["supplier", "Rome", "late", "delay", "shipment", "Super 150s"],
}

SYSTEMS = [
    "Cegid",
    "InventoryDB",
    "PricingDB",
    "ManufacturingDB",
    "ShippingDB",
    "ERP",
    "PIM",
    "CRM",
    "Milan workshop",
    "Rome supplier",
]


def infer_store(title: str, body: str) -> Optional[str]:
    combined = (title + " " + body).lower()
    for store in STORES:
        if store.lower() in combined:
            return store
        for p in store.split():
            if p.lower() in combined:
                return store
    return None


def infer_risk_topic(title: str, body: str) -> Optional[str]:
    combined = (title + " " + body).lower()
    best_topic = None
    best_hits = 0

    for topic, keywords in RISK_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw.lower() in combined)
        if hits > best_hits:
            best_hits = hits
            best_topic = topic

    return best_topic


def infer_systems(body: str) -> list:
    lower = body.lower()
    found = []
    for sys in SYSTEMS:
        if sys.lower() in lower:
            found.append(sys)
    return found


def enrich_signal(signal: CanonicalSignal) -> CanonicalSignal:
    cleaned = clean_email_body(signal.body_raw)

    signal.body_clean = cleaned["clean"]
    signal.body_latest_message = cleaned["main"]
    signal.body_history = cleaned["history"]
    signal.body = cleaned["main"] or signal.body_raw

    signal.privacy_flag = "anonymized"
    signal.anonymization_status = cleaned["anonymization_status"]

    store = infer_store(signal.title, signal.body_latest_message)
    risk_topic = infer_risk_topic(signal.title, signal.body_latest_message)
    systems = infer_systems(signal.body_latest_message)

    signal.store = store
    signal.risk_topic = risk_topic
    signal.systems_mentioned = systems

    return signal
