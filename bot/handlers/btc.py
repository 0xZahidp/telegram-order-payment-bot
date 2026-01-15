from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from telegram.error import BadRequest, Forbidden

from bot.utils.constants import *
from bot.services.order_service import OrderService
from bot.services.admin_service import AdminService
from config.settings import Settings

import re


# =====================================================
# TXID VALIDATION (BTC HEX OR SCANNER LINK)
# =====================================================
TXID_HEX_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")
TXID_URL_REGEX = re.compile(
    r"(blockchain\.com|btc\.com|blockchair\.com|mempool\.space)",
    re.IGNORECASE,
)


def extract_txid(text: str) -> str | None:
    text = text.strip()

    if TXID_HEX_REGEX.match(text):
        return text

    if TXID_URL_REGEX.search(text):
        return text

    return None


# =====================================================
# START BTC PAYMENT
# =====================================================
async def start_btc_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "₿ *BTC Payment*\n\n"
        "Please enter your *Order ID* to continue.",
        parse_mode="Markdown",
    )
    return STATE_PAYMENT_ORDER_ID


# =====================================================
# COLLECT ORDER ID
# =====================================================
async def collect_btc_order_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip()

    order_service: OrderService = context.bot_data["order_service"]

    if not order_service.order_exists(order_id):
        await update.message.reply_text(
            "❌ *Invalid Order ID*\n\n"
            "Please check and enter a valid Order ID.",
            parse_mode="Markdown",
        )
        return STATE_PAYMENT_ORDER_ID

    context.user_data["order_id"] = order_id

    await update.message.reply_text(
        "💵 Please enter your order subtotal in USD.\n"
        "_(Do not include BTC fee)_",
        parse_mode="Markdown",
    )
    return STATE_BTC_SUBTOTAL


# =====================================================
# COLLECT SUBTOTAL
# =====================================================
async def collect_btc_subtotal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        subtotal = float(update.message.text.strip())
        if subtotal <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid USD amount.")
        return STATE_BTC_SUBTOTAL

    settings: Settings = context.bot_data["settings"]

    fee = round(subtotal * (settings.BTC_FEE_PERCENT / 100), 2)
    total = round(subtotal + fee, 2)

    context.user_data["btc_payment"] = {
        "Subtotal USD": subtotal,
        "BTC Fee USD": fee,
        "Total USD": total,
    }

    await update.message.reply_text(
        "💵 *Payment Summary*\n\n"
        f"🆔 Order ID: `{context.user_data['order_id']}`\n"
        f"*Total to Send:* {total} USD\n\n"
        f"📥 *BTC Wallet: (Tap on address to copy)*\n"
        f"`{settings.BTC_WALLET}`\n\n"
        "⚠️ Network fees are paid by sender.\n\n"
        "📌 Send BTC and reply with *TXID only*\n"
        "Example:\n"
        "`4e3f2a1b0c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d`\n"
        "or scanner link.\n\n"
        "❌ Do NOT send screenshots or media.",
        parse_mode="Markdown",
    )

    return STATE_BTC_TXID


# =====================================================
# COLLECT TXID (STRICT)
# =====================================================
async def collect_btc_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # ❌ Block media
    if (
        message.photo
        or message.video
        or message.document
        or message.voice
        or message.video_note
        or message.audio
    ):
        await message.reply_text(
            "⚠️ Invalid submission.\n\n"
            "Please send **TXID text or scanner link only**.\n"
            "Media files are not accepted.",
            parse_mode="Markdown",
        )
        return STATE_BTC_TXID

    txid = extract_txid(message.text or "")
    if not txid:
        await message.reply_text(
            "❌ Invalid BTC TXID.\n\n"
            "Send a valid TXID or blockchain scanner link.",
        )
        return STATE_BTC_TXID

    user = update.effective_user
    payment = context.user_data.get("btc_payment")
    order_id = context.user_data.get("order_id")

    if not payment or not order_id:
        await update.message.reply_text("❌ Session expired. Please start again.")
        return ConversationHandler.END

    order_service: OrderService = context.bot_data["order_service"]
    admin_service: AdminService = context.bot_data["admin_service"]
    settings: Settings = context.bot_data["settings"]

    # ✅ Save BTC payment
    order_service.create_btc_payment({
        "Order ID": order_id,
        "Subtotal USD": payment["Subtotal USD"],
        "BTC Fee USD": payment["BTC Fee USD"],
        "Total USD": payment["Total USD"],
        "BTC Wallet": settings.BTC_WALLET,
        "TXID": txid,
        "Status": "Pending",
    })

    # =================================================
    # 🔔 NOTIFY ALL ADMINS (SAFE)
    # =================================================
    admin_message = (
        "₿ New BTC Payment Submitted\n\n"
        f"Order ID: {order_id}\n"
        f"User ID: {user.id}\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"Subtotal: {payment['Subtotal USD']} USD\n"
        f"Fee: {payment['BTC Fee USD']} USD\n"
        f"Total: {payment['Total USD']} USD\n"
        f"TXID:\n{txid}"
    )

    for admin in admin_service.get_active_admins():
        admin_id = admin.get("Telegram ID")
        try:
            await context.bot.send_message(
                chat_id=int(admin_id),
                text=admin_message,
            )
        except (BadRequest, Forbidden):
            continue
        except Exception as e:
            context.application.logger.error(
                f"Admin notify failed ({admin_id}): {e}"
            )

    # =================================================
    # ✅ CONFIRM USER
    # =================================================
    from bot.handlers.user import build_main_menu

    await update.message.reply_text(
        "✅ *BTC payment submitted successfully!*\n\n"
        "Our admins will verify your transaction shortly.\n\n"
        "⬇️ What would you like to do next?",
        parse_mode="Markdown",
        reply_markup=build_main_menu(user.id, admin_service),
    )

    context.user_data.clear()
    return ConversationHandler.END
