"""
Per-field input validators.

Each validator returns the normalized value on success, or raises
ValueError with a user-friendly message on failure. The handler layer
catches ValueError and shows the message to the user, then keeps the
FSM in the same state so they can retry.
"""

import re


# Standard RFC-5322-ish email regex (good enough for intake forms,
# not for cryptographic validation).
_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

# Phone: allow +, digits, spaces, dashes, parens; require 8+ digits total.
_PHONE_RE = re.compile(r"^\+?[\d\s\-()]{8,}$")


def validate_full_name(raw: str) -> str:
    """Strip whitespace, require at least 2 chars and a space (first + last)."""
    cleaned = " ".join(raw.split())
    if len(cleaned) < 2:
        raise ValueError("Name is too short")
    return cleaned


def validate_email(raw: str) -> str:
    """Lowercase and validate against a permissive email regex."""
    cleaned = raw.strip().lower()
    if not _EMAIL_RE.match(cleaned):
        raise ValueError("Invalid email format")
    return cleaned


def validate_phone(raw: str) -> str:
    """Validate phone format and normalize to digits-only with leading +."""
    cleaned = raw.strip()
    if not _PHONE_RE.match(cleaned):
        raise ValueError("Invalid phone format")
    digits = re.sub(r"\D", "", cleaned)
    if len(digits) < 8:
        raise ValueError("Phone number too short")
    return "+" + digits


def validate_message(raw: str) -> str:
    """Free-form message — just trim and cap length to prevent abuse."""
    cleaned = raw.strip()
    if len(cleaned) > 2000:
        cleaned = cleaned[:2000] + "…"
    return cleaned or "(no message)"
