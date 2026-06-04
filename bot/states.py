"""
FSM states for the form intake flow.

Add a new state here when you want to add a new field to the form.
You will also need to:
  1. Add a handler in `bot/handlers.py` (the order is the form order)
  2. Add the user-facing prompt text in `bot/messages.py`
  3. (Optional) Add a validator in `bot/validators.py`
"""

from aiogram.fsm.state import State, StatesGroup


class FormFlow(StatesGroup):
    """The default form: name → email → phone → message → confirm."""

    waiting_for_full_name = State()
    waiting_for_email = State()
    waiting_for_phone = State()
    waiting_for_message = State()
    waiting_for_confirmation = State()


# Ordered list of fields stored in the submission record.
# Keep in sync with your Google Sheet header row.
SUBMISSION_FIELDS = ("full_name", "email", "phone", "message")
