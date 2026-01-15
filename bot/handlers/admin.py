# Admin handlers (root & admin)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from bot.utils.constants import *
from bot.services.admin_service import AdminService


# =====================================================
# ADMIN MANAGEMENT MENU
# =====================================================
def build_admin_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(BTN_ADD_ADMIN, callback_data=CB_ADD_ADMIN)],
        [InlineKeyboardButton(BTN_REMOVE_ADMIN, callback_data=CB_REMOVE_ADMIN)],
        [InlineKeyboardButton(BTN_LIST_ADMINS, callback_data=CB_LIST_ADMINS)],
        [InlineKeyboardButton(BTN_BACK_TO_MAIN, callback_data=CB_BACK_TO_MAIN)],
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# SHOW ADMIN MENU AGAIN (HELPER)
# =====================================================
async def show_admin_menu_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 *Admin Management*\n\nChoose an action:",
        reply_markup=build_admin_menu(),
        parse_mode="Markdown",
    )


# =====================================================
# OPEN ADMIN MANAGEMENT
# =====================================================
async def open_admin_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()
    admin_service: AdminService = context.bot_data["admin_service"]

    # 🔐 Root-only access
    if not admin_service.is_root(query.from_user.id):
        await query.edit_message_text("❌ Access denied.")
        return ConversationHandler.END

    await query.edit_message_text(
        "🛠 *Admin Management*\n\nChoose an action:",
        reply_markup=build_admin_menu(),
        parse_mode="Markdown",
    )

    return ConversationHandler.END


# =====================================================
# ADD ADMIN
# =====================================================
async def start_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    await query.edit_message_text(
        "➕ *Add Admin*\n\n"
        "Send the *Telegram ID* of the user\n"
        "OR forward a message from the user.",
        parse_mode="Markdown",
    )

    return STATE_ADD_ADMIN_ID


async def finalize_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_service: AdminService = context.bot_data["admin_service"]

    # Forwarded message → extract ID
    if update.message.forward_from:
        telegram_id = update.message.forward_from.id
        username = update.message.forward_from.username or ""
    else:
        try:
            telegram_id = int(update.message.text.strip())
            username = ""
        except (ValueError, AttributeError):
            await update.message.reply_text("❌ Invalid Telegram ID.")
            return STATE_ADD_ADMIN_ID

    try:
        admin_service.add_admin(
            telegram_id=telegram_id,
            username=username,
            added_by=update.effective_user.id,
        )
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return ConversationHandler.END

    await update.message.reply_text(
        f"✅ Admin added successfully.\nTelegram ID: `{telegram_id}`",
        parse_mode="Markdown",
    )

    await show_admin_menu_again(update, context)
    return ConversationHandler.END


# =====================================================
# REMOVE ADMIN
# =====================================================
async def start_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    await query.edit_message_text(
        "➖ *Remove Admin*\n\nSend the *Telegram ID* to disable.",
        parse_mode="Markdown",
    )

    return STATE_REMOVE_ADMIN_SELECT


async def finalize_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_service: AdminService = context.bot_data["admin_service"]

    try:
        telegram_id = int(update.message.text.strip())
    except (ValueError, AttributeError):
        await update.message.reply_text("❌ Invalid Telegram ID.")
        return STATE_REMOVE_ADMIN_SELECT

    # Safety: prevent root removal
    if admin_service.is_root(telegram_id):
        await update.message.reply_text("❌ Root admin cannot be removed.")
        return ConversationHandler.END

    try:
        admin_service.disable_admin(telegram_id)
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return ConversationHandler.END

    await update.message.reply_text(
        f"✅ Admin `{telegram_id}` has been disabled.",
        parse_mode="Markdown",
    )

    await show_admin_menu_again(update, context)
    return ConversationHandler.END


# =====================================================
# LIST ADMINS
# =====================================================
async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    admin_service: AdminService = context.bot_data["admin_service"]
    admins = admin_service.get_active_admins()

    if not admins:
        text = "No active admins found."
    else:
        lines = ["📋 *Active Admins*\n"]
        for admin in admins:
            lines.append(
                f"• `{admin.get('Telegram ID')}` ({admin.get('Type')})"
            )
        text = "\n".join(lines)

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=build_admin_menu(),
    )
