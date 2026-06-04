"""
All command, message, and callback handlers.

The form is a straightforward FSM:

  /start → waiting_for_full_name → ... → waiting_for_confirmation → submit

Validation lives in `bot/validators.py`. User-facing strings are in
`bot/messages.py`. The actual storage and sheets writes are in
`db/storage.py` and `services/sheets.py` respectively — handlers just
orchestrate.
"""

from datetime import datetime, timezone

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot import messages, validators
from bot.keyboards import confirmation_keyboard
from bot.states import FormFlow
from db.storage import Storage
from services.notifications import notify_admin_new_submission
from services.sheets import SheetsService

router = Router(name="form-intake")


# ---------------------------------------------------------------------------
# Start + cancel
# ---------------------------------------------------------------------------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, storage: Storage) -> None:
    """Greet the user and begin the form. Block duplicate submissions."""
    user_id = message.from_user.id  # type: ignore[union-attr]

    if await storage.has_submission(user_id):
        await message.answer(messages.ALREADY_SUBMITTED)
        return

    await state.clear()
    await state.set_state(FormFlow.waiting_for_full_name)
    await message.answer(messages.WELCOME)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(messages.CANCELLED)


# ---------------------------------------------------------------------------
# Form steps
# ---------------------------------------------------------------------------

@router.message(FormFlow.waiting_for_full_name)
async def step_full_name(message: Message, state: FSMContext) -> None:
    try:
        full_name = validators.validate_full_name(message.text or "")
    except ValueError:
        await message.answer(messages.INVALID_NAME)
        return

    await state.update_data(full_name=full_name)
    await state.set_state(FormFlow.waiting_for_email)
    await message.answer(messages.ASK_EMAIL)


@router.message(FormFlow.waiting_for_email)
async def step_email(message: Message, state: FSMContext) -> None:
    try:
        email = validators.validate_email(message.text or "")
    except ValueError:
        await message.answer(messages.INVALID_EMAIL)
        return

    await state.update_data(email=email)
    await state.set_state(FormFlow.waiting_for_phone)
    await message.answer(messages.ASK_PHONE)


@router.message(FormFlow.waiting_for_phone)
async def step_phone(message: Message, state: FSMContext) -> None:
    try:
        phone = validators.validate_phone(message.text or "")
    except ValueError:
        await message.answer(messages.INVALID_PHONE)
        return

    await state.update_data(phone=phone)
    await state.set_state(FormFlow.waiting_for_message)
    await message.answer(messages.ASK_MESSAGE)


@router.message(FormFlow.waiting_for_message)
async def step_message(message: Message, state: FSMContext) -> None:
    msg = validators.validate_message(message.text or "")
    await state.update_data(message=msg)

    data = await state.get_data()
    summary = messages.CONFIRM_TEMPLATE.format(**data)

    await state.set_state(FormFlow.waiting_for_confirmation)
    await message.answer(summary, reply_markup=confirmation_keyboard())


# ---------------------------------------------------------------------------
# Confirmation callbacks
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "form:submit", FormFlow.waiting_for_confirmation)
async def cb_submit(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    storage: Storage,
    sheets: SheetsService,
    admin_chat_id: int,
) -> None:
    user = callback.from_user
    data = await state.get_data()
    timestamp = datetime.now(timezone.utc).isoformat()

    submission = {
        "timestamp": timestamp,
        "user_id": user.id,
        "username": user.username or "",
        **data,
    }

    try:
        await storage.save_submission(submission)
        await sheets.append_submission(submission)
    except Exception as exc:
        logger.exception("Failed to persist submission: {}", exc)
        await callback.message.answer(messages.ERROR_GENERIC)  # type: ignore[union-attr]
        await callback.answer()
        return

    await notify_admin_new_submission(bot, admin_chat_id, submission)

    await callback.message.edit_reply_markup(reply_markup=None)  # type: ignore[union-attr]
    await callback.message.answer(messages.SUBMITTED)  # type: ignore[union-attr]
    await callback.answer("Submitted ✓")
    await state.clear()

    logger.info("Submission stored for user {} ({})", user.id, user.username)


@router.callback_query(F.data == "form:restart", FormFlow.waiting_for_confirmation)
async def cb_restart(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FormFlow.waiting_for_full_name)
    await callback.message.edit_reply_markup(reply_markup=None)  # type: ignore[union-attr]
    await callback.message.answer(messages.WELCOME)  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data == "form:cancel", FormFlow.waiting_for_confirmation)
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)  # type: ignore[union-attr]
    await callback.message.answer(messages.CANCELLED)  # type: ignore[union-attr]
    await callback.answer()


# ---------------------------------------------------------------------------
# Admin commands
# ---------------------------------------------------------------------------

@router.message(Command("admin"))
async def cmd_admin(
    message: Message,
    storage: Storage,
    admin_chat_id: int,
) -> None:
    if message.from_user.id != admin_chat_id:  # type: ignore[union-attr]
        await message.answer(messages.ADMIN_ONLY)
        return

    stats = await storage.get_stats()
    await message.answer(messages.ADMIN_STATS_TEMPLATE.format(**stats))
