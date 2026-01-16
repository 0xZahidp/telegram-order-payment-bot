from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.utils.constants import *
from bot.services.admin_service import AdminService
from bot.services.order_service import OrderService


# =======================
# PAYMENT HANDLERS
# =======================

from bot.handlers.btc import (
    start_btc_payment,
    collect_btc_order_id,
    collect_btc_subtotal,
    collect_btc_txid,
)

from bot.handlers.eth import (
    start_eth_payment,
    collect_eth_order_id,
    collect_eth_subtotal,
    collect_eth_txid,
)

from bot.handlers.usdt import (
    start_usdt_payment,
    collect_usdt_order_id,
    collect_usdt_subtotal,
    collect_usdt_txid,
)

# =====================================================
# MAIN MENU BUILDER
# =====================================================
def build_main_menu(user_id: int, admin_service: AdminService) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(BTN_MEDIA_CHANNEL, url="https://t.me/+37NU62X0ftpiNDQx")],
        [
            InlineKeyboardButton(
                BTN_SIGNAL_GROUP,
                url="https://signal.group/#CjQKIJR_5Zmk1qdqfpASTNk_8ND1oWVWmZanqwErgpt83z6iEhCWUWPKmPTdjRgTWhSy5NSP",
            ),
            InlineKeyboardButton(
                BTN_SIGNAL_DM,
                url="https://signal.me/#eu/ddxqlF3A-LcvVwgcnNx0X01D13tM9AwNOJ16gmH_xiQ5evPTS8xEUKlZmkOo_Me4",
            ),
        ],
        [InlineKeyboardButton(BTN_LIVE_MENU, callback_data=CB_LIVE_MENU)],
        [
            InlineKeyboardButton(BTN_HOW_TO_ORDER, callback_data=CB_HOW_TO_ORDER),
            InlineKeyboardButton(BTN_SUBMIT_ORDER, callback_data=CB_SUBMIT_ORDER),
        ],
        [
            InlineKeyboardButton(BTN_PAY_BTC, callback_data=CB_PAY_BTC),
            InlineKeyboardButton(BTN_PAY_ETH, callback_data=CB_PAY_ETH),
            InlineKeyboardButton(BTN_PAY_USDT, callback_data=CB_PAY_USDT),
        ],
        [
            InlineKeyboardButton(BTN_ABOUT, callback_data=CB_ABOUT),
            InlineKeyboardButton(BTN_SUPPORT, callback_data=CB_SUPPORT),
        ],
    ]

    if admin_service.is_root(user_id):
        keyboard.append(
            [InlineKeyboardButton(BTN_ADMIN_MANAGEMENT, callback_data=CB_ADMIN_MANAGEMENT)]
        )

    return InlineKeyboardMarkup(keyboard)


def build_order_submission_menu(order_id: str) -> InlineKeyboardMarkup:
    """Menu shown after order submission with payment options and Main Menu button"""
    keyboard = [
        [
            InlineKeyboardButton(BTN_PAY_BTC, callback_data=CB_PAY_BTC),
            InlineKeyboardButton(BTN_PAY_ETH, callback_data=CB_PAY_ETH),
            InlineKeyboardButton(BTN_PAY_USDT, callback_data=CB_PAY_USDT),
        ],
        [InlineKeyboardButton("🏠 Main Menu", callback_data=f"{CB_BACK_TO_MAIN}:{order_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_order_main_menu(user_id: int, admin_service: AdminService, order_id: str) -> InlineKeyboardMarkup:
    """Main menu for users who just submitted an order (keeps order ID in context)"""
    keyboard = [
        [InlineKeyboardButton(BTN_MEDIA_CHANNEL, url="https://t.me/+37NU62X0ftpiNDQx")],
        [
            InlineKeyboardButton(
                BTN_SIGNAL_GROUP,
                url="https://signal.group/#CjQKIJR_5Zmk1qdqfpASTNk_8ND1oWVWmZanqwErgpt83z6iEhCWUWPKmPTdjRgTWhSy5NSP",
            ),
            InlineKeyboardButton(
                BTN_SIGNAL_DM,
                url="https://signal.me/#eu/ddxqlF3A-LcvVwgcnNx0X01D13tM9AwNOJ16gmH_xiQ5evPTS8xEUKlZmkOo_Me4",
            ),
        ],
        [InlineKeyboardButton(BTN_LIVE_MENU, callback_data=CB_LIVE_MENU)],
        [
            InlineKeyboardButton(BTN_HOW_TO_ORDER, callback_data=CB_HOW_TO_ORDER),
            InlineKeyboardButton(BTN_SUBMIT_ORDER, callback_data=CB_SUBMIT_ORDER),
        ],
        [
            InlineKeyboardButton(BTN_PAY_BTC, callback_data=f"{CB_PAY_BTC}:{order_id}"),
            InlineKeyboardButton(BTN_PAY_ETH, callback_data=f"{CB_PAY_ETH}:{order_id}"),
            InlineKeyboardButton(BTN_PAY_USDT, callback_data=f"{CB_PAY_USDT}:{order_id}"),
        ],
        [
            InlineKeyboardButton(BTN_ABOUT, callback_data=CB_ABOUT),
            InlineKeyboardButton(BTN_SUPPORT, callback_data=CB_SUPPORT),
        ],
    ]

    if admin_service.is_root(user_id):
        keyboard.append(
            [InlineKeyboardButton(BTN_ADMIN_MANAGEMENT, callback_data=CB_ADMIN_MANAGEMENT)]
        )

    return InlineKeyboardMarkup(keyboard)


# =====================================================
# /start
# =====================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin_service: AdminService = context.bot_data["admin_service"]
    
    # Check if we're coming from an order submission context
    order_id = None
    if update.callback_query and ':' in update.callback_query.data:
        # Extract order ID from callback data if present
        try:
            order_id = update.callback_query.data.split(':')[1]
        except:
            order_id = None
    # Also check context.user_data as a fallback
    elif context.user_data.get('current_order_id'):
        order_id = context.user_data.get('current_order_id')

    text = (
        f"👋 Welcome, {user.first_name}!\n\n"
        "Use the menu below to navigate.\n"
        "All orders and payments are reviewed manually."
    )
    
    if order_id:
        text += f"\n\n📦 Your current Order ID: `{order_id}`"

    if update.message:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=build_main_menu(user.id, admin_service),
        )
    else:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=build_order_main_menu(user.id, admin_service, order_id) if order_id else build_main_menu(user.id, admin_service),
        )


# =====================================================
# ORDER FLOW
# =====================================================
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📝 *Submit Order*\n\n"
        "Please paste your full order in the following format:\n\n"
        "```\n"
        "1x LEMON BISCOTTI (Smalls) $525\n"
        "1x GLITTER BOMB (Indoor) $675\n"
        "```\n\n"
        "You can list multiple items line by line.",
        parse_mode="Markdown",
    )
    return STATE_ORDER_TEXT

async def collect_order_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_text"] = update.message.text

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("₿ BTC", callback_data="PM_BTC"),
            InlineKeyboardButton("Ξ ETH", callback_data="PM_ETH"),
            InlineKeyboardButton("💎 USDT", callback_data="PM_USDT"),
        ]
    ])

    await update.message.reply_text(
        "💳 Select payment method (for order tracking only).",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    return STATE_PAYMENT_METHOD


async def collect_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["payment_method"] = query.data.replace("PM_", "")
    await query.edit_message_text("👤 Enter *Receiver Name*.", parse_mode="Markdown")
    return STATE_RECEIVER_NAME


async def collect_receiver_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["receiver_name"] = update.message.text
    await update.message.reply_text("📍 Enter *Delivery Address*.", parse_mode="Markdown")
    return STATE_ADDRESS


async def collect_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text("🚚 Enter *Carrier* or type N/A.", parse_mode="Markdown")
    return STATE_CARRIER


async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # -------------------------
    # SAFETY CHECK
    # -------------------------
    if "order_text" not in context.user_data:
        await update.message.reply_text(
            "❌ Your session has expired. Please start again."
        )
        return ConversationHandler.END

    # Save carrier
    context.user_data["carrier"] = update.message.text.strip()

    order_service: OrderService = context.bot_data["order_service"]
    admin_service: AdminService = context.bot_data["admin_service"]

    # 🔥 FIX: DEFINE THESE
    telegram_username = f"@{user.username}" if user.username else "N/A"
    telegram_name = user.full_name or user.first_name or "Unknown"

    # -------------------------
    # CREATE ORDER
    # -------------------------
    order_id = order_service.generate_next_order_id()

    order_payload = {
        "Order ID": order_id,
        "Telegram ID": str(user.id),
        "Telegram Username": telegram_username,
        "Telegram Name": telegram_name,
        "Order Text": context.user_data.get("order_text", ""),
        "Payment Method": context.user_data.get("payment_method", ""),
        "Receiver Name": context.user_data.get("receiver_name", ""),
        "Address": context.user_data.get("address", ""),
        "Carrier": context.user_data.get("carrier", ""),
        "Status": "Pending Payment",
    }

    order_service.create_order(order_payload)

    # -------------------------
    # NOTIFY ADMINS (SAFE)
    # -------------------------
    admin_message = (
    "📦 *New Order Submitted*\n\n"
    f"🆔 Order ID: `{order_id}`\n"
    f"👤 User: [{telegram_name}](tg://user?id={user.id})\n"
    f"🆔 User ID: `{user.id}`\n"
    f"💳 Payment Method: {order_payload['Payment Method']}\n"
    f"🚚 Carrier: {order_payload['Carrier']}\n\n"
    f"📝 Order Details:\n{order_payload['Order Text']}"
)


    admins = admin_service.get_active_admins()

    for admin in admins:
        admin_id = admin.get("Telegram ID")
        try:
            await context.bot.send_message(
                chat_id=int(admin_id),
                text=admin_message,
                parse_mode="Markdown",
            )
        except Exception:
            # Admin may not have started the bot – ignore safely
            continue

    # -------------------------
    # CONFIRM USER WITH PAYMENT OPTIONS AND ORDER ID
    # -------------------------
    await update.message.reply_text(
        "✅ *Order submitted successfully!*\n\n"
        f"🆔 Order ID: `{order_id}`\n"
        f"💳 Selected Payment: *{order_payload['Payment Method']}*\n\n"
        "⚠️ *Important:* Your order is NOT paid yet.\n"
        "Please make payment using the payment buttons below.\n\n"
        "⬇️ What would you like to do next?",
        parse_mode="Markdown",
        reply_markup=build_order_submission_menu(order_id),
    )

    # -------------------------
    # CLEAN SESSION
    # -------------------------
    context.user_data.clear()
    return ConversationHandler.END



# =====================================================
# CONVERSATION HANDLERS
# =====================================================
order_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_order, pattern=f"^{CB_SUBMIT_ORDER}$")],
    states={
        STATE_ORDER_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_order_text)
        ],
        STATE_PAYMENT_METHOD: [
            CallbackQueryHandler(collect_payment_method, pattern="^PM_(BTC|ETH|USDT)$")
        ],
        STATE_RECEIVER_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_receiver_name)
        ],
        STATE_ADDRESS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_address)
        ],
        STATE_CARRIER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, finalize_order)
        ],
    },
    fallbacks=[],
)

# Modified payment handlers to handle order ID in callback data
btc_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_btc_payment, pattern=f"^{CB_PAY_BTC}(?::.*)?$")],
    states={
        STATE_PAYMENT_ORDER_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_btc_order_id)
        ],
        STATE_BTC_SUBTOTAL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_btc_subtotal)
        ],
        STATE_BTC_TXID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_btc_txid)
        ],
    },
    fallbacks=[
        CallbackQueryHandler(start_btc_payment, pattern=f"^{CB_PAY_BTC}(?::.*)?$")
    ],
    allow_reentry=True,   # 🔥 THIS LINE FIXES FREEZE
)

eth_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_eth_payment, pattern=f"^{CB_PAY_ETH}(?::.*)?$")],
    states={
        STATE_PAYMENT_ORDER_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_eth_order_id)
        ],
        STATE_ETH_SUBTOTAL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_eth_subtotal)
        ],
        STATE_ETH_TXID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_eth_txid)
        ],
    },
    fallbacks=[
        CallbackQueryHandler(start_eth_payment, pattern=f"^{CB_PAY_ETH}(?::.*)?$")
    ],
    allow_reentry=True,   # 🔥 THIS LINE FIXES FREEZE
)

usdt_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_usdt_payment, pattern=f"^{CB_PAY_USDT}(?::.*)?$")],
    states={
        STATE_PAYMENT_ORDER_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_usdt_order_id)
        ],
        STATE_USDT_SUBTOTAL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_usdt_subtotal)
        ],
        STATE_USDT_TXID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_usdt_txid)
        ],
    },
    fallbacks=[
        CallbackQueryHandler(start_usdt_payment, pattern=f"^{CB_PAY_USDT}(?::.*)?$")
    ],
    allow_reentry=True,   # 🔥 THIS LINE FIXES FREEZE
)

# =====================================================
# MENU PAGES
# =====================================================

async def how_to_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    admin_service: AdminService = context.bot_data["admin_service"]

    text = (
        "📖 *How to Submit an Order*\n\n"
        "1️⃣ Tap *Submit Order*\n"
        "2️⃣ Copy & paste your order details from the *Live Menu* section\n"
        "3️⃣ Enter the *Recipient Name*\n"
        "4️⃣ Enter the *Delivery Address*\n"
        "5️⃣ Enter *Preferred Carrier* (if any)\n\n"
        "✅ Orders are reviewed manually."
    )

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=build_main_menu(query.from_user.id, admin_service),
    )



async def show_live_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    menu_service = context.bot_data["menu_service"]
    admin_service: AdminService = context.bot_data["admin_service"]

    blocks = menu_service.get_menu_text_blocks()

    # Determine which menu to show based on context
    order_id = None
    # Check if we're coming from an order submission context
    if query.message.reply_markup:
        for row in query.message.reply_markup.inline_keyboard:
            for button in row:
                if button.callback_data and ':' in button.callback_data:
                    try:
                        order_id = button.callback_data.split(':')[1]
                        break
                    except:
                        continue
    
    # Edit original message with first block
    reply_markup = build_order_main_menu(query.from_user.id, admin_service, order_id) if order_id else build_main_menu(query.from_user.id, admin_service)
    
    await query.edit_message_text(
        blocks[0],
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

    # Send remaining blocks as new messages
    for block in blocks[1:]:
        await query.message.reply_text(
            block,
            parse_mode="Markdown",
        )



async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    admin_service: AdminService = context.bot_data["admin_service"]

    await query.edit_message_text(
        "ℹ️ *About / Rules*\n\n"
        "This bot is used for directing traffic, showing Menu and taking shipped orders",
        parse_mode="Markdown",
        reply_markup=build_main_menu(query.from_user.id, admin_service),
    )


async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    admin_service: AdminService = context.bot_data["admin_service"]

    await query.edit_message_text(
        "🆘 *Support*\n\n"
        "To Get Verified Please send a Verification Video with Packs or Bags and DC written on a Paper to @DCLA\\_Orders\n\n"
        "To contact admin message @DCLA\\_Orders or Tap the Signal DM Link.",
        parse_mode="Markdown",
        reply_markup=build_main_menu(query.from_user.id, admin_service),
    )

# =====================================================
# HANDLE BACK TO MAIN MENU (SIMPLIFIED)
# =====================================================
async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    admin_service: AdminService = context.bot_data["admin_service"]
    
    # Extract order ID from callback data
    order_id = None
    if ':' in query.data:
        try:
            order_id = query.data.split(':')[1]
        except:
            order_id = None
    
    text = (
        f"👋 Welcome back, {user.first_name}!\n\n"
        "Use the menu below to navigate.\n"
        "All orders and payments are reviewed manually."
    )
    
    if order_id:
        text += f"\n\n📦 Your current Order ID: `{order_id}`"
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=build_order_main_menu(user.id, admin_service, order_id) if order_id else build_main_menu(user.id, admin_service),
    )

# =====================================================
# MAIN MENU ROUTER - SIMPLIFIED
# =====================================================
async def main_menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Extract the base callback data without order ID for pattern matching
    callback_data = query.data
    base_callback = callback_data.split(':')[0] if ':' in callback_data else callback_data

    if base_callback == CB_LIVE_MENU:
        await show_live_menu(update, context)
        return

    if base_callback == CB_HOW_TO_ORDER:
        await how_to_order(update, context)
        return

    if base_callback == CB_ABOUT:
        await show_about(update, context)
        return

    if base_callback == CB_SUPPORT:
        await show_support(update, context)
        return
    
    if base_callback == CB_BACK_TO_MAIN:
        # Handle back to main separately
        await handle_back_to_main(update, context)
        return

# =====================================================
# REGISTER USER HANDLERS
# =====================================================
def get_user_handlers():
    return [
        CommandHandler("start", start),
        order_conv,
        btc_conv,
        eth_conv,
        usdt_conv,
        CallbackQueryHandler(
            main_menu_router,
            pattern=f"^({CB_LIVE_MENU}|{CB_HOW_TO_ORDER}|{CB_ABOUT}|{CB_SUPPORT})(?::.*)?$"
        ),
        CallbackQueryHandler(
            handle_back_to_main,
            pattern=f"^{CB_BACK_TO_MAIN}(?::.*)?$"
        ),
    ]