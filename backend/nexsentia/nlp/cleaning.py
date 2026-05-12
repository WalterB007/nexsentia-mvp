import re
from typing import Tuple


EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_RE = re.compile(r'(\+?\d[\d\s\-\(\)]{7,}\d)')


def strip_html_basic(text: str) -> str:
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p\s*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def strip_disclaimers(text: str) -> str:
    patterns = [
        r'This message and any attachments.*',
        r'Ce message et ses pièces jointes.*',
    ]
    for p in patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE | re.DOTALL)
    return text.strip()


def split_thread(text: str) -> Tuple[str, str]:
    lines = text.splitlines()
    main_lines = []
    history_lines = []
    in_history = False

    for line in lines:
        stripped = line.strip()
        if not in_history and (
            (stripped.startswith("On ") and " wrote:" in stripped)
            or stripped.startswith("From:")
            or stripped.startswith("Sent:")
            or stripped.startswith("De :")
        ):
            in_history = True

        if in_history:
            history_lines.append(line)
        else:
            main_lines.append(line)

    return "\n".join(main_lines).strip(), "\n".join(history_lines).strip()


def anonymize_pii(text: str) -> str:
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    return text


def clean_email_body(text: str) -> dict:
    no_html = strip_html_basic(text)
    no_disclaimer = strip_disclaimers(no_html)
    main, history = split_thread(no_disclaimer)

    main = re.sub(r'\n{3,}', '\n\n', main).strip()
    history = re.sub(r'\n{3,}', '\n\n', history).strip()

    anonymized_main = anonymize_pii(main)
    anonymized_history = anonymize_pii(history)

    return {
        "clean": no_disclaimer,
        "main": anonymized_main,
        "history": anonymized_history,
        "anonymization_status": "anonymized",
    }
