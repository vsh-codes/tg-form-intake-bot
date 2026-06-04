"""
Unit tests for the input validators.

Run with:
    pytest tests/
"""

import pytest

from bot.validators import (
    validate_email,
    validate_full_name,
    validate_message,
    validate_phone,
)


# ---------------------------------------------------------------------------
# validate_full_name
# ---------------------------------------------------------------------------

class TestValidateFullName:
    def test_normal_name(self) -> None:
        assert validate_full_name("John Smith") == "John Smith"

    def test_collapses_whitespace(self) -> None:
        assert validate_full_name("  John   Smith  ") == "John Smith"

    def test_too_short_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_full_name("J")

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_full_name("")


# ---------------------------------------------------------------------------
# validate_email
# ---------------------------------------------------------------------------

class TestValidateEmail:
    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("a@b.co", "a@b.co"),
            ("First.Last@example.com", "first.last@example.com"),
            (" user@DOMAIN.ORG ", "user@domain.org"),
        ],
    )
    def test_valid_emails(self, raw: str, expected: str) -> None:
        assert validate_email(raw) == expected

    @pytest.mark.parametrize(
        "raw",
        [
            "not-an-email",
            "@example.com",
            "user@",
            "user@example",
            "",
            "user @example.com",
        ],
    )
    def test_invalid_emails(self, raw: str) -> None:
        with pytest.raises(ValueError):
            validate_email(raw)


# ---------------------------------------------------------------------------
# validate_phone
# ---------------------------------------------------------------------------

class TestValidatePhone:
    def test_with_plus(self) -> None:
        assert validate_phone("+380 50 123 45 67") == "+380501234567"

    def test_without_plus(self) -> None:
        assert validate_phone("380 50 123 45 67") == "+380501234567"

    def test_with_parens_and_dashes(self) -> None:
        assert validate_phone("+1 (415) 555-2671") == "+14155552671"

    @pytest.mark.parametrize("raw", ["123", "abc", "", "++++"])
    def test_too_short_or_invalid_raises(self, raw: str) -> None:
        with pytest.raises(ValueError):
            validate_phone(raw)


# ---------------------------------------------------------------------------
# validate_message
# ---------------------------------------------------------------------------

class TestValidateMessage:
    def test_normal(self) -> None:
        assert validate_message("Hello, I would like to apply.") == \
            "Hello, I would like to apply."

    def test_empty_returns_placeholder(self) -> None:
        assert validate_message("") == "(no message)"
        assert validate_message("   ") == "(no message)"

    def test_truncates_long(self) -> None:
        long = "x" * 3000
        result = validate_message(long)
        assert len(result) <= 2001  # 2000 + ellipsis
        assert result.endswith("…")
