"""
Google Sheets integration.

Uses a service-account JSON key to authenticate and append rows to a
worksheet. All blocking gspread calls are pushed to a thread pool so
the asyncio event loop stays responsive even if Google's API is slow.

The header row is created on first run if the sheet is empty.
"""

import asyncio
from pathlib import Path
from typing import Any

import gspread
from google.oauth2.service_account import Credentials
from loguru import logger


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Column order — must match the keys produced by handlers.cb_submit.
COLUMNS = ("timestamp", "user_id", "username", "full_name", "email", "phone", "message")


class SheetsService:
    """Thin async wrapper around a gspread worksheet."""

    def __init__(
        self,
        credentials_path: Path,
        sheet_id: str,
        worksheet_name: str = "Applications",
    ) -> None:
        self._credentials_path = credentials_path
        self._sheet_id = sheet_id
        self._worksheet_name = worksheet_name
        self._worksheet: gspread.Worksheet | None = None

    async def initialize(self) -> None:
        """Authenticate, open the sheet, ensure the header row exists."""
        await asyncio.to_thread(self._initialize_sync)

    def _initialize_sync(self) -> None:
        creds = Credentials.from_service_account_file(
            str(self._credentials_path),
            scopes=SCOPES,
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(self._sheet_id)

        try:
            worksheet = spreadsheet.worksheet(self._worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=self._worksheet_name,
                rows=1000,
                cols=len(COLUMNS),
            )

        # Create header row if missing
        first_row = worksheet.row_values(1)
        if not first_row:
            worksheet.append_row(list(COLUMNS))
            logger.info("Created header row in sheet {}", self._worksheet_name)

        self._worksheet = worksheet
        logger.info("Google Sheets connected: {}", self._worksheet_name)

    async def append_submission(self, submission: dict[str, Any]) -> None:
        """Append a submission as a new row, in the order defined by COLUMNS."""
        if self._worksheet is None:
            raise RuntimeError("SheetsService not initialized")

        row = [str(submission.get(col, "")) for col in COLUMNS]
        await asyncio.to_thread(self._worksheet.append_row, row)
