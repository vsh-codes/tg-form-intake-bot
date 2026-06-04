"""
Entry point for the Telegram form intake bot.

Wires together aiogram, the storage layer, and the Google Sheets service,
then starts long-polling. Graceful shutdown on SIGINT/SIGTERM.
"""

import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from bot.handlers import router as main_router
from config import settings
from db.storage import Storage
from services.sheets import SheetsService


def configure_logging() -> None:
    """Set up Loguru with rotation and configurable level."""
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}:{function}:{line}</cyan> | "
            "{message}"
        ),
        colorize=True,
    )
    logger.add(
        "logs/bot.log",
        level=settings.log_level,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
    )


async def main() -> None:
    configure_logging()
    logger.info("Starting tg-form-intake-bot")

    # Initialize storage layer (creates DB file if missing)
    storage = Storage(settings.database_path)
    await storage.initialize()

    # Initialize Google Sheets service (validates auth + sheet access)
    sheets = SheetsService(
        credentials_path=settings.google_service_account_path,
        sheet_id=settings.google_sheet_id,
        worksheet_name=settings.google_worksheet_name,
    )
    await sheets.initialize()

    # Set up bot and dispatcher
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Inject dependencies into handlers via workflow_data
    dp["storage"] = storage
    dp["sheets"] = sheets
    dp["admin_chat_id"] = settings.admin_chat_id

    dp.include_router(main_router)

    logger.info("Bot is ready, starting polling")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await storage.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down on interrupt")
