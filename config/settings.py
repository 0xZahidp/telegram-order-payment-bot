import os
from dotenv import load_dotenv
from typing import Dict, Any

from bot.services.google_sheets import GoogleSheetsService

load_dotenv()


class Settings:
    """
    Central configuration loader.
    - Loads ENV variables
    - Loads dynamic values from Google Sheets (Settings tab)
    """

    def __init__(self):
        # ===== ENV VALUES (STATIC) =====
        self.BOT_TOKEN = self._require_env("BOT_TOKEN")
        self.ADMIN_CHAT_ID = int(self._require_env("ADMIN_CHAT_ID"))

        self.GOOGLE_SHEET_ID = self._require_env("GOOGLE_SHEET_ID")
        self.SERVICE_ACCOUNT_JSON_PATH = self._require_env(
            "SERVICE_ACCOUNT_JSON_PATH"
        )

        self.EMERGENCY_ROOT_ADMIN_ID = os.getenv(
            "EMERGENCY_ROOT_ADMIN_ID"
        )

        # ===== GOOGLE SHEETS (DYNAMIC) =====
        self._sheets_service = GoogleSheetsService(
            sheet_id=self.GOOGLE_SHEET_ID,
            service_account_path=self.SERVICE_ACCOUNT_JSON_PATH,
        )

        self.dynamic: Dict[str, Any] = {}
        self.reload_dynamic_settings()

    # -------------------------
    # ENV HELPERS
    # -------------------------
    @staticmethod
    def _require_env(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"Missing required ENV variable: {key}")
        return value

    # -------------------------
    # GOOGLE SHEETS SETTINGS
    # -------------------------
    def reload_dynamic_settings(self) -> None:
        """
        Loads key-value pairs from the `Settings` sheet.
        Expected headers: key | value
        """
        rows = self._sheets_service.read_sheet("Settings")

        settings = {}
        for row in rows:
            key = row.get("key")
            value = row.get("value")

            if not key:
                continue

            settings[str(key).strip()] = self._parse_value(value)

        self.dynamic = settings

    @staticmethod
    def _parse_value(value: Any):
        """
        Try to cast numeric values automatically.
        """
        if value is None:
            return None

        value = str(value).strip()

        if value.isdigit():
            return int(value)

        try:
            return float(value)
        except ValueError:
            return value

    # -------------------------
    # SAFE GETTER
    # -------------------------
    def get(self, key: str, default=None):
        return self.dynamic.get(key, default)

    # =========================
    # BUSINESS SETTINGS
    # =========================

    @property
    def MARKUP_USD(self) -> float:
        return float(self.get("MARKUP_USD", 0))

    # ===== BTC =====
    @property
    def BTC_FEE_PERCENT(self) -> float:
        return float(self.get("BTC_FEE_PERCENT", 3))

    @property
    def BTC_WALLET(self) -> str:
        return str(self.get("BTC_WALLET", ""))

    # ===== ETH =====
    @property
    def ETH_FEE_PERCENT(self) -> float:
        return float(self.get("ETH_FEE_PERCENT", 3))

    @property
    def ETH_WALLET(self) -> str:
        return str(self.get("ETH_WALLET", ""))

    # ===== USDT =====
    @property
    def USDT_FEE_PERCENT(self) -> float:
        return float(self.get("USDT_FEE_PERCENT", 3))

    @property
    def USDT_WALLET(self) -> str:
        return str(self.get("USDT_WALLET", ""))

    # ===== GENERAL =====
    @property
    def CURRENCY(self) -> str:
        return str(self.get("CURRENCY", "USD"))
    
