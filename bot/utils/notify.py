from telegram.error import BadRequest, Forbidden
from bot.services.admin_service import AdminService


async def notify_all_admins(context, message: str):
    """
    Send message to all active admins.
    Never crashes the caller.
    """
    admin_service: AdminService = context.bot_data["admin_service"]
    admins = admin_service.get_active_admins()

    for admin in admins:
        admin_id = admin.get("Telegram ID")

        try:
            await context.bot.send_message(
                chat_id=int(admin_id),
                text=message,
            )
        except (BadRequest, Forbidden):
            # ❌ Admin never started bot or blocked it
            # We silently ignore to avoid crashing flows
            continue
        except Exception as e:
            # Log but never crash
            context.application.logger.error(
                f"Admin notify failed for {admin_id}: {e}"
            )
