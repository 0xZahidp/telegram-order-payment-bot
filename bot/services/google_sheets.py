import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional


class GoogleSheetsService:
    """
    Central Google Sheets service.
    Handles auth, read, append, update.
    Backward-compatible with all services.
    """

    def __init__(self, sheet_id: str, service_account_path: str):
        self.sheet_id = sheet_id
        self.service_account_path = service_account_path
        self.client = self._authorize()
        self.spreadsheet = self.client.open_by_key(self.sheet_id)

    # =====================================================
    # AUTH
    # =====================================================
    def _authorize(self) -> gspread.Client:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = Credentials.from_service_account_file(
            self.service_account_path,
            scopes=scopes,
        )

        return gspread.authorize(credentials)

    # =====================================================
    # READ (DICT BASED)
    # =====================================================
    def read_sheet(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        Reads a sheet and returns list of dicts using header row.
        """
        worksheet = self.spreadsheet.worksheet(sheet_name)
        return worksheet.get_all_records() or []

    # ✅ BACKWARD COMPATIBILITY
    def get_rows(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        Alias for read_sheet()
        """
        return self.read_sheet(sheet_name)

    # =====================================================
    # READ (RAW VALUES)
    # =====================================================
    def get_values(self, sheet_name: str) -> List[List[Any]]:
        """
        Reads raw values (rows) from a sheet.
        """
        worksheet = self.spreadsheet.worksheet(sheet_name)
        return worksheet.get_all_values() or []

    # =====================================================
    # APPEND (DICT SAFE)
    # =====================================================
    def append_row(self, sheet_name: str, row: Dict[str, Any]) -> None:
        """
        Appends a row using column headers order.
        """
        worksheet = self.spreadsheet.worksheet(sheet_name)
        headers = worksheet.row_values(1)

        # Auto-create header if empty
        if not headers:
            headers = list(row.keys())
            worksheet.insert_row(headers, 1)

        values = [row.get(header, "") for header in headers]
        worksheet.append_row(values, value_input_option="USER_ENTERED")

    # =====================================================
    # UPDATE SINGLE ROW
    # =====================================================
    def update_row(
        self,
        sheet_name: str,
        row_index: int,
        updates: Dict[str, Any],
    ) -> None:
        """
        Updates specific columns in a given row index (1-based).
        """
        worksheet = self.spreadsheet.worksheet(sheet_name)
        headers = worksheet.row_values(1)

        for column_name, new_value in updates.items():
            if column_name not in headers:
                continue

            col_index = headers.index(column_name) + 1
            worksheet.update_cell(row_index, col_index, new_value)

    # =====================================================
    # UPDATE FULL SHEET (🔥 REQUIRED)
    # =====================================================
    def update(self, sheet_name: str, rows: List[Dict[str, Any]]) -> None:
        """
        Replaces entire sheet content using dict rows.
        Used by AdminService disable logic.
        """
        worksheet = self.spreadsheet.worksheet(sheet_name)

        if not rows:
            return

        headers = list(rows[0].keys())
        values = [headers]

        for row in rows:
            values.append([row.get(h, "") for h in headers])

        worksheet.clear()
        worksheet.update("A1", values)

    # =====================================================
    # FIND ROW BY VALUE
    # =====================================================
    def find_row_by_value(
        self,
        sheet_name: str,
        column_name: str,
        value: Any,
    ) -> Optional[int]:
        """
        Finds first row index where column == value.
        Returns row index or None.
        """
        worksheet = self.spreadsheet.worksheet(sheet_name)
        headers = worksheet.row_values(1)

        if column_name not in headers:
            return None

        col_index = headers.index(column_name) + 1
        cell = worksheet.find(str(value), in_column=col_index)

        return cell.row if cell else None
