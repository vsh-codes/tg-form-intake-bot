"""
Inline and reply keyboards used in the form flow.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def confirmation_keyboard() -> InlineKeyboardMarkup:
    """Submit / Edit / Cancel buttons shown before final submission."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Submit", callback_data="form:submit"),
                InlineKeyboardButton(text="✏️ Edit", callback_data="form:restart"),
            ],
            [
                InlineKeyboardButton(text="❌ Cancel", callback_data="form:cancel"),
            ],
        ]
    )
