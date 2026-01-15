from typing import Dict
from datetime import datetime

from bot.services.google_sheets import GoogleSheetsService
from bot.utils.helpers import utc_now_iso


class OrderService:
    ORDERS_SHEET = "Orders"
    BTC_SHEET = "BTC_Payments"
    ETH_SHEET = "ETH_Payments"
    USDT_SHEET = "USDT_Payments"

    def __init__(self, sheets: GoogleSheetsService):
        """
        Central order & payment service.
        Uses a shared GoogleSheetsService instance.
        """
        self.sheets = sheets

    # =====================================================
    # ORDERS
    # =====================================================
    def create_order(self, data: Dict) -> None:
        data["Status"] = "Pending"
        data["Timestamp"] = utc_now_iso()
        self.sheets.append_row(self.ORDERS_SHEET, data)

    def order_exists(self, order_id: str) -> bool:
        """
        Robust Order ID validation using raw values.
        """
        try:
            rows = self.sheets.get_values(self.ORDERS_SHEET)
            if not rows or len(rows) < 2:
                return False

            order_id = order_id.strip().upper()

            for row in rows[1:]:  # skip header
                if not row:
                    continue

                sheet_order_id = str(row[0]).strip().upper()
                if sheet_order_id == order_id:
                    return True

            return False

        except Exception as e:
            print(f"[OrderService] order_exists ERROR: {e}")
            return False

    def generate_next_order_id(self) -> str:
        """
        Generates a unique Order ID.
        Format: ORD-YYYYMMDD-XXXX
        Safe across restarts.
        """
        today = datetime.utcnow().strftime("%Y%m%d")
        prefix = f"ORD-{today}-"

        try:
            rows = self.sheets.get_values(self.ORDERS_SHEET)
            max_counter = 0

            for row in rows[1:]:
                if not row:
                    continue

                order_id = str(row[0]).strip()
                if order_id.startswith(prefix):
                    try:
                        counter = int(order_id.split("-")[-1])
                        max_counter = max(max_counter, counter)
                    except ValueError:
                        continue

            next_counter = max_counter + 1
            return f"{prefix}{next_counter:04d}"

        except Exception as e:
            print(f"[OrderService] generate_next_order_id ERROR: {e}")
            return f"{prefix}0001"

    # =====================================================
    # BTC PAYMENTS
    # =====================================================
    def create_btc_payment(self, data: Dict) -> None:
        data["Status"] = "Pending"
        data["Timestamp"] = utc_now_iso()
        self.sheets.append_row(self.BTC_SHEET, data)

    # =====================================================
    # ETH PAYMENTS
    # =====================================================
    def create_eth_payment(self, data: Dict) -> None:
        data["Status"] = "Pending"
        data["Timestamp"] = utc_now_iso()
        self.sheets.append_row(self.ETH_SHEET, data)

    # =====================================================
    # USDT PAYMENTS
    # =====================================================
    def create_usdt_payment(self, data: Dict) -> None:
        data["Status"] = "Pending"
        data["Timestamp"] = utc_now_iso()
        self.sheets.append_row(self.USDT_SHEET, data)
