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
# TXID VALIDATION (ETH HEX OR ETHERSCAN LINK)
# =====================================================
TXID_HEX_REGEX = re.compile(r"^0x[a-fA-F0-9]{64}$")
TXID_URL_REGEX = re.compile(
    r"(etherscan\.io)",
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
# START ETH PAYMENT
# =====================================================
async def start_eth_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "Ξ *ETH Payment*\n\n"
        "Please enter your *Order ID* to continue.",
        parse_mode="Markdown",
    )
    return STATE_PAYMENT_ORDER_ID


# =====================================================
# COLLECT ORDER ID
# =====================================================
async def collect_eth_order_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip()
    order_service: OrderService = context.bot_data["order_service"]

    if not order_service.order_exists(order_id):
        await update.message.reply_text(
            "❌ *Invalid Order ID*\n\nPlease enter a valid Order ID.",
            parse_mode="Markdown",
        )
        return STATE_PAYMENT_ORDER_ID

    context.user_data["order_id"] = order_id

    await update.message.reply_text(
        "💵 Please enter your order subtotal in USD.\n"
        "_(Do not include ETH fee)_",
        parse_mode="Markdown",
    )
    return STATE_ETH_SUBTOTAL


# =====================================================
# COLLECT SUBTOTAL (✅ 3% ETH FEE ADDED)
# =====================================================
async def collect_eth_subtotal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        subtotal = float(update.message.text.strip())
        if subtotal <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid USD amount.")
        return STATE_ETH_SUBTOTAL

    settings: Settings = context.bot_data["settings"]
    eth_wallet = settings.ETH_WALLET

    fee = round(subtotal * (settings.ETH_FEE_PERCENT / 100), 2)
    total = round(subtotal + fee, 2)

    context.user_data["eth_payment"] = {
        "Subtotal USD": subtotal,
        "ETH Fee USD": fee,
        "Total USD": total,
        "ETH Wallet": eth_wallet,
    }

    await update.message.reply_text(
        "💵 *Payment Summary*\n\n"
        f"🆔 Order ID: `{context.user_data['order_id']}`\n"
        f"*Total to Send:* {total} USD\n\n"
        f"📥 *ETH Wallet: (Tap on address to copy)*\n"
        f"`{eth_wallet}`\n\n"
        "⚠️ Gas fees are paid by sender.\n\n"
        "📌 Send ETH and reply with *TXID only*\n"
        "Example:\n"
        "`0x5e8f9c2b9a4a7d1f6c0b3e1a9f0d7c8b2e4a6f9c3d1e8b7a6c5d4e3f2a1b0`\n"
        "or Etherscan link.\n\n"
        "❌ Do NOT send screenshots or media.",
        parse_mode="Markdown",
    )

    return STATE_ETH_TXID


# =====================================================
# COLLECT TXID (STRICT)
# =====================================================
async def collect_eth_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            "Please send **TXID text or Etherscan link only**.\n"
            "Media files are not accepted.",
            parse_mode="Markdown",
        )
        return STATE_ETH_TXID

    txid = extract_txid(message.text or "")
    if not txid:
        await message.reply_text(
            "❌ Invalid TXID.\n\n"
            "Send a valid ETH TXID or Etherscan link.",
        )
        return STATE_ETH_TXID

    user = update.effective_user
    order_id = context.user_data.get("order_id")
    payment = context.user_data.get("eth_payment")

    if not order_id or not payment:
        await update.message.reply_text("❌ Session expired. Please start again.")
        return ConversationHandler.END

    order_service: OrderService = context.bot_data["order_service"]
    admin_service: AdminService = context.bot_data["admin_service"]

    # ✅ Save ETH payment with fee breakdown
    order_service.create_eth_payment({
        "Order ID": order_id,
        "Subtotal USD": payment["Subtotal USD"],
        "ETH Fee USD": payment["ETH Fee USD"],
        "Total USD": payment["Total USD"],
        "ETH Wallet": payment["ETH Wallet"],
        "TXID": txid,
        "Status": "Pending",
    })

    # =================================================
    # 🔔 NOTIFY ADMINS
    # =================================================
    admin_message = (
        "Ξ New ETH Payment Submitted\n\n"
        f"Order ID: {order_id}\n"
        f"User ID: {user.id}\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"Subtotal: {payment['Subtotal USD']} USD\n"
        f"Fee: {payment['ETH Fee USD']} USD\n"
        f"Total: {payment['Total USD']} USD\n"
        f"TXID:\n{txid}"
    )

    for admin in admin_service.get_active_admins():
        try:
            await context.bot.send_message(
                chat_id=int(admin["Telegram ID"]),
                text=admin_message,
            )
        except (BadRequest, Forbidden):
            continue
        except Exception as e:
            context.application.logger.error(
                f"Admin notify failed ({admin['Telegram ID']}): {e}"
            )

    from bot.handlers.user import build_main_menu

    await update.message.reply_text(
        "✅ *ETH payment submitted successfully!*\n\n"
        "Our admins will verify your transaction shortly.\n\n"
        "⬇️ What would you like to do next?",
        parse_mode="Markdown",
        reply_markup=build_main_menu(user.id, admin_service),
    )

    context.user_data.clear()
    return ConversationHandler.END
# =====================================================
