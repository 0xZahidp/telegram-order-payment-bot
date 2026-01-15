from collections import defaultdict
from typing import List

from bot.services.google_sheets import GoogleSheetsService
from config.settings import Settings


class MenuService:
    """
    Handles Live Menu logic:
    - Reads InventoryList
    - Applies markup
    - Groups by category
    - Formats display text
    (Quantity is intentionally NOT shown)
    """

    SHEET_NAME = "InventoryList"

    def __init__(self, sheets: GoogleSheetsService, settings: Settings):
        self.sheets = sheets
        self.settings = settings

    def get_menu_text_blocks(self) -> List[str]:
        """
        Returns menu text split into safe Telegram-sized blocks.
        """
        items = self.sheets.read_sheet(self.SHEET_NAME)

        # HARD SAFETY
        if not items:
            return []

        grouped = defaultdict(list)

        # -------------------------
        # READ & PROCESS ROWS
        # -------------------------
        for item in items:
            try:
                name = str(item.get("Item Name", "")).strip()
                category = str(item.get("Category", "Other")).strip()
                price_raw = str(item.get("Price Base", "")).strip()

                # Skip invalid rows
                if not name or not price_raw:
                    continue

                # Clean price (remove $ if present)
                price_clean = price_raw.replace("$", "").strip()
                base_price = float(price_clean)

                # Apply markup
                client_price = round(
                    base_price + float(self.settings.MARKUP_USD),
                    2,
                )

                grouped[category].append((name, client_price))

            except Exception:
                # Skip malformed rows safely
                continue

        if not grouped:
            return []

        # -------------------------
        # BUILD MENU TEXT
        # -------------------------
        blocks: List[str] = []
        current_block = "📋 *Live Menu*\n"
        max_length = 3500  # Telegram safe margin

        for category, items in grouped.items():
            section = f"\n\n📦 *{category}*\n"

            for name, price in items:
                # Format price as $525 or $525.5
                formatted_price = (
                    int(price) if price.is_integer() else price
                )
                line = f"• *{name}* — ${formatted_price}\n"
                section += line

            if len(current_block) + len(section) > max_length:
                blocks.append(current_block)
                current_block = section
            else:
                current_block += section

        if current_block.strip():
            blocks.append(current_block)

        return blocks
