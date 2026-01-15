from bot.services.google_sheets import GoogleSheetsService

class SettingsService:
    SHEET_NAME = "Settings"

    def __init__(self, sheets: GoogleSheetsService):
        self.sheets = sheets

    def get(self, key: str, default=None):
        rows = self.sheets.read_sheet(self.SHEET_NAME)
        for row in rows:
            if row.get("key") == key:
                return row.get("value")
        return default
