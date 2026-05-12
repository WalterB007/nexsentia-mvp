from typing import List
from ..models.clustering import Cluster


GENERIC_WORDS = {
    "nexsentia", "&gt", "side", "quick", "thanks",
    "client", "clients", "issue", "issues", "operational",
    "proactively", "adjust", "fittings", "dates",
    "latest", "bespoke",
}


def _clean_keywords(keywords: List[str]) -> List[str]:
    return [k for k in keywords if k.lower() not in GENERIC_WORDS]


def _make_business_title(cluster: Cluster) -> str:
    topic = cluster.dominant_risk_topic or "Operational Topic"
    stores = cluster.stores
    cleaned_keywords = _clean_keywords(cluster.keywords)

    if topic == "Order Promise Risk":
        base = "Client promises at risk for bespoke orders"
    elif topic == "Packaging Shortage":
        base = "Packaging shortage impacting outbound shipments"
    elif topic == "Shipping Blockage":
        base = "Blocked shipments between Milan and French stores"
    elif topic == "Supply Delay":
        base = "Supply delays on Super 150s impacting Milan production"
    elif topic == "Manufacturing Quality":
        base = "Quality pressure on recent Milan workshop deliveries"
    else:
        base = "Operational topic detected by Nexsentia"

    if stores:
        if len(stores) == 1:
            base += f" – {stores[0]}"
        else:
            base += f" – several stores ({', '.join(stores[:3])}...)"

    if cleaned_keywords:
        base += f" [{', '.join(cleaned_keywords[:3])}]"

    return base


def _make_executive_summary(cluster: Cluster) -> str:
    topic = cluster.dominant_risk_topic or "an operational topic"
    n_signals = cluster.size
    stores = cluster.stores
    systems = cluster.systems
    score = cluster.risk_score

    parts = []

    # Phrase 1 : synthèse globale
    if stores:
        if len(stores) == 1:
            parts.append(
                f"Nexsentia has grouped {n_signals} signals related to {topic} "
                f"for {stores[0]}."
            )
        else:
            parts.append(
                f"Nexsentia has grouped {n_signals} signals related to {topic} "
                f"across {len(stores)} stores."
            )
    else:
        parts.append(
            f"Nexsentia has grouped {n_signals} signals related to {topic}."
        )

    # Phrase 2 : systèmes
    if systems:
        parts.append(
            f"The topic involves {len(systems)} systems: {', '.join(systems[:5])}."
        )

    # Phrase 3 : score
    parts.append(
        f"The current Nexsentia Risk Score for this cluster is {score:.1f}."
    )

    return " ".join(parts)


def _make_recommended_action(cluster: Cluster) -> str:
    topic = cluster.dominant_risk_topic or ""

    if topic == "Order Promise Risk":
        return (
            "Review all impacted bespoke orders for the next two weeks, "
            "update promises proactively for VIP clients and align Milan workshop, "
            "stores and logistics on a common view of committed dates."
        )

    if topic == "Supply Delay":
        return (
            "Organise a short cross-functional review with the Rome supplier, "
            "Milan workshop and logistics to secure fabric availability and "
            "confirm shipment dates for the most critical shades."
        )

    if topic == "Packaging Shortage":
        return (
            "Confirm incoming deliveries from CartaPack, prioritise outbound "
            "shipments for fittings already scheduled and consider temporary "
            "alternative packaging options."
        )

    if topic == "Shipping Blockage":
        return (
            "Request firm dates for all blocked parcels, communicate clearly "
            "with stores on expected arrival windows and adjust fittings when needed."
        )

    if topic == "Manufacturing Quality":
        return (
            "Review the last batches from Milan, identify recurring alteration "
            "requests from stores and adjust quality checks before dispatch."
        )

    # fallback
    return (
        "Review the underlying signals with the relevant stakeholders and "
        "decide whether this topic requires a dedicated mitigation plan."
    )


def _make_confidence_level(cluster: Cluster) -> str:
    # Heuristique simple basée sur volume et Risk Score
    if cluster.size >= 10 or cluster.risk_score >= 60:
        return "high"
    if cluster.size >= 5 or cluster.risk_score >= 40:
        return "medium"
    return "low"


def enrich_clusters_business(clusters: List[Cluster]) -> List[Cluster]:
    """
    Enrichit les clusters avec un titre business, un résumé exécutif,
    une recommandation et un niveau de confiance.
    """
    for c in clusters:
        c.keywords = _clean_keywords(c.keywords)
        c.business_title = _make_business_title(c)
        c.executive_summary = _make_executive_summary(c)
        c.recommended_action = _make_recommended_action(c)
        c.confidence_level = _make_confidence_level(c)

    return clusters
