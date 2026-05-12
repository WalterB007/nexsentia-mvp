from datetime import datetime
from typing import Dict
from ..models.canonical import CanonicalSignal


def _extract_plain_body(message: Dict) -> str:
    body = message.get("body", {})
    content = body.get("content", "") or ""
    return content


def _extract_participants(message: Dict) -> list:
    participants = []
    sender = message.get("from")
    if sender and sender.get("emailAddress"):
        addr = sender["emailAddress"].get("address")
        if addr:
            participants.append(addr)

    for field in ("toRecipients", "ccRecipients", "bccRecipients"):
        for entry in message.get(field, []) or []:
            addr = entry.get("emailAddress", {}).get("address")
            if addr and addr not in participants:
                participants.append(addr)
    return participants


def outlook_message_to_signal(msg: Dict) -> CanonicalSignal:
    sent = msg.get("sentDateTime") or msg.get("receivedDateTime")
    if sent:
        event_ts = datetime.fromisoformat(sent.replace("Z", "+00:00"))
    else:
        event_ts = datetime.utcnow()

    body_text = _extract_plain_body(msg)
    participants = _extract_participants(msg)

    return CanonicalSignal(
        signal_id=f"outlook-{msg['id']}",
        source_system="Outlook",
        source_object_type="email",
        source_object_id=msg["id"],
        event_timestamp=event_ts,

        title=msg.get("subject", "") or "",
        body=body_text,
        body_raw=body_text,
        body_clean="",
        body_latest_message="",
        body_history="",

        language="en",
        participants=participants,
        thread_id=msg.get("conversationId"),

        store=None,
        risk_topic=None,
        systems_mentioned=[],

        privacy_flag="contains_pii_possible",
        anonymization_status="not_processed",

        raw_metadata={
            "internetMessageId": msg.get("internetMessageId"),
            "conversationId": msg.get("conversationId"),
        },
    )
