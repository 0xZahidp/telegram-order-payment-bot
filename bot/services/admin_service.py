from typing import List, Dict, Optional
from datetime import datetime


class AdminService:
    """
    Admin & Root Admin RBAC logic.
    Uses Google Sheet `Admins`
    """

    SHEET_NAME = "Admins"

    def __init__(self, sheets, emergency_root_id: Optional[str]):
        self.sheets = sheets
        self.emergency_root_id = int(emergency_root_id) if emergency_root_id else None

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================
    def _read_all_rows(self) -> List[Dict]:
        return self.sheets.read_sheet(self.SHEET_NAME) or []

    def _normalize(self, value) -> str:
        return str(value).strip().lower()

    def _is_active(self, row: Dict) -> bool:
        return self._normalize(row.get("Status", "")) == "active"

    def _get_type(self, row: Dict) -> str:
        return self._normalize(row.get("Type", ""))

    # =====================================================
    # ROOT CHECK
    # =====================================================
    def is_root(self, telegram_id: int) -> bool:
        # Emergency root ALWAYS root
        if self.emergency_root_id and telegram_id == self.emergency_root_id:
            return True

        for row in self._read_all_rows():
            if (
                str(row.get("Telegram ID")) == str(telegram_id)
                and self._get_type(row) == "root"
                and self._is_active(row)
            ):
                return True

        return False

    # =====================================================
    # ADMIN CHECK
    # =====================================================
    def is_admin(self, telegram_id: int) -> bool:
        if self.is_root(telegram_id):
            return True

        for row in self._read_all_rows():
            if (
                str(row.get("Telegram ID")) == str(telegram_id)
                and self._is_active(row)
            ):
                return True

        return False

    # =====================================================
    # LIST ADMINS
    # =====================================================
    def get_active_admins(self) -> List[Dict]:
        rows = self._read_all_rows()

        if not rows and self.emergency_root_id:
            return [{
                "Telegram ID": str(self.emergency_root_id),
                "Type": "root",
                "Status": "active",
            }]

        return [row for row in rows if self._is_active(row)]

    # =====================================================
    # ADD ADMIN (✅ FIXED)
    # =====================================================
    def add_admin(self, telegram_id: int, username: str, added_by: int):
        if self.is_admin(telegram_id):
            raise ValueError("User is already an admin.")

        row = {
            "Telegram ID": str(telegram_id),
            "Username": username or "",
            "Type": "admin",
            "Status": "active",
            "Added By": str(added_by),
            "Added At": datetime.utcnow().isoformat(),
        }

        # ✅ CORRECT METHOD
        self.sheets.append_row(self.SHEET_NAME, row)

    # =====================================================
    # DISABLE ADMIN
    # =====================================================
    def disable_admin(self, telegram_id: int):
        if self.emergency_root_id and telegram_id == self.emergency_root_id:
            raise ValueError("Emergency root admin cannot be disabled.")

        rows = self._read_all_rows()

        for index, row in enumerate(rows):
            if str(row.get("Telegram ID")) == str(telegram_id):

                if self._get_type(row) == "root":
                    raise ValueError("Root admin cannot be disabled.")

                rows[index]["Status"] = "inactive"
                self.sheets.update(self.SHEET_NAME, rows)
                return

        raise ValueError("Admin not found.")
