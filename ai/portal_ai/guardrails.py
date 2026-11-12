"""Guardrails applied to everything that leaves the device or changes data."""
from __future__ import annotations
import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
MEDICAL = re.compile(r"\b(chest pain|faint|dizz|injur|sharp pain|can't breathe|palpitation)", re.I)


def redact(text: str) -> str:
    """Remove contact details and ID numbers before text is sent to a hosted model."""
    text = _SSN.sub("[ID]", text)
    text = _EMAIL.sub("[EMAIL]", text)
    return _PHONE.sub("[PHONE]", text)


def needs_medical_referral(text: str) -> bool:
    return bool(MEDICAL.search(text))


MEDICAL_NOTE = ("That sounds like something to check with a doctor before training again. "
                "I can adjust the plan to rest and mobility in the meantime.")
