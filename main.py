# Entry point for the Telegram Bot
import logging

from telegram.ext import (
    Application,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config.settings import Settings
from bot.services.google_sheets import GoogleSheetsService
from bot.services.admin_service import AdminService
from bot.services.menu_service import MenuService
from bot.services.order_service import OrderService
from bot.services.settings_service import SettingsService  # ✅ NEW

from bot.handlers.user import get_user_handlers
from bot.handlers.admin import (
    open_admin_management,
    start_add_admin,
    finalize_add_admin,
    start_remove_admin,
    finalize_remove_admin,
    list_admins,
)

from bot.utils.constants import (
    CB_ADMIN_MANAGEMENT,
    CB_ADD_ADMIN,
    CB_REMOVE_ADMIN,
    CB_LIST_ADMINS,
    CB_BACK,
    STATE_ADD_ADMIN_ID,
    STATE_REMOVE_ADMIN_SELECT,
)

# -------------------------
# LOGGING
# -------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# -------------------------
# MAIN ENTRY
# -------------------------
def main():
    # 1️⃣ Load static settings (.env)
    settings = Settings()

    # 2️⃣ Google Sheets service
    sheets_service = GoogleSheetsService(
        sheet_id=settings.GOOGLE_SHEET_ID,
        service_account_path=settings.SERVICE_ACCOUNT_JSON_PATH,
    )

    # 3️⃣ Dynamic settings service (Google Sheet → Settings)
    settings_service = SettingsService(sheets=sheets_service)  # ✅ NEW

    # 4️⃣ Domain services
    admin_service = AdminService(
        sheets=sheets_service,
        emergency_root_id=settings.EMERGENCY_ROOT_ADMIN_ID,
    )

    menu_service = MenuService(
        sheets=sheets_service,
        settings=settings,  # ⚠️ unchanged (backward compatible)
    )

    order_service = OrderService(
        sheets=sheets_service,
    )

    # 5️⃣ Telegram application
    application = Application.builder().token(settings.BOT_TOKEN).build()

    # 6️⃣ Inject shared services
    application.bot_data["settings"] = settings              # ✅ keep
    application.bot_data["settings_service"] = settings_service  # ✅ NEW
    application.bot_data["sheets"] = sheets_service
    application.bot_data["admin_service"] = admin_service
    application.bot_data["menu_service"] = menu_service
    application.bot_data["order_service"] = order_service

    # --------------------------------------------------
    # 7️⃣ ADMIN CONVERSATION HANDLER
    # --------------------------------------------------
    admin_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                open_admin_management,
                pattern=f"^{CB_ADMIN_MANAGEMENT}$",
            ),
            CallbackQueryHandler(
                start_add_admin,
                pattern=f"^{CB_ADD_ADMIN}$",
            ),
            CallbackQueryHandler(
                start_remove_admin,
                pattern=f"^{CB_REMOVE_ADMIN}$",
            ),
        ],
        states={
            STATE_ADD_ADMIN_ID: [
                MessageHandler(
                    filters.TEXT | filters.FORWARDED,
                    finalize_add_admin,
                )
            ],
            STATE_REMOVE_ADMIN_SELECT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    finalize_remove_admin,
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(
                open_admin_management,
                pattern=f"^{CB_BACK}$",
            ),
        ],
        allow_reentry=True,
    )

    application.add_handler(admin_conversation)

    # --------------------------------------------------
    # 8️⃣ ADMIN BUTTON (NO STATE)
    # --------------------------------------------------
    application.add_handler(
        CallbackQueryHandler(
            list_admins,
            pattern=f"^{CB_LIST_ADMINS}$",
        )
    )

    # -------------------------
    # 9️⃣ USER HANDLERS
    # -------------------------
    for handler in get_user_handlers():
        application.add_handler(handler)

    # -------------------------
    # 🔟 START BOT
    # -------------------------
    logger.info("🚀 Bot started successfully")
    application.run_polling()


if __name__ == "__main__":
    main()
