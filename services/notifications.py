"""
Admin notification helpers.

Kept as a separate module so it's trivial to extend (Slack, email, etc.)
without touching the handler code.
"""

from typing import Any

from aiogram import Bot
from loguru import logger

from bot import messages


async def notify_admin_new_submission(
    bot: Bot,
    admin_chat_id: int,
    submission: dict[str, Any],
) -> None:
    """Send the admin a formatted message about the new submission."""
    text = messages.ADMIN_NEW_SUBMISSION_TEMPLATE.format(
        username=submission.get("username") or "(none)",
        user_id=submission["user_id"],
        full_name=submission["full_name"],
        email=submission["email"],
        phone=submission["phone"],
        message=submission["message"],
    )
    try:
        await bot.send_message(admin_chat_id, text)
    except Exception as exc:
        # Don't fail the user flow if admin notification fails —
        # the submission is already in Sheets and SQLite.
        logger.warning("Failed to notify admin: {}", exc)
