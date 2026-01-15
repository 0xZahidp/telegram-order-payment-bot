"""
Central place for all constants:
- Button texts
- Callback data
- Conversation states
"""

# =========================
# MAIN MENU BUTTON TEXT
# =========================

BTN_MEDIA_CHANNEL = "🎬 View Our Media Channel"
BTN_SIGNAL_GROUP = "🔒 Signal Group Private Menu"
BTN_SIGNAL_DM = "💬 Signal DM"
BTN_LIVE_MENU = "📊 Live Menu"
BTN_HOW_TO_ORDER = "📖 How to Order"
BTN_SUBMIT_ORDER = "📝 Submit Order"
BTN_PAY_BTC = "₿ Pay BTC"
BTN_PAY_ETH = "Ξ Pay ETH"
BTN_PAY_USDT = "💎 Pay USDT"
BTN_ABOUT = "ℹ️ About / Rules"
BTN_SUPPORT = "🆘 Support"

# Root-only
BTN_ADMIN_MANAGEMENT = "🛠 Admin Management"

CB_PM_BTC = "pm_btc"
CB_PM_ETH = "pm_eth"
CB_PM_USDT = "pm_usdt"

# =========================
# ADMIN MANAGEMENT BUTTONS
# =========================

BTN_ADD_ADMIN = "➕ Add Admin"
BTN_REMOVE_ADMIN = "➖ Remove Admin"
BTN_LIST_ADMINS = "📋 List Admins"
BTN_BACK = "⬅️ Back"

# =========================
# NAVIGATION
# =========================
BTN_BACK_TO_MAIN = "⬅️ Back to Main"

# =========================
# CALLBACK DATA KEYS
# =========================

CB_MEDIA_CHANNEL = "cb_media_channel"
CB_SIGNAL_GROUP = "cb_signal_group"
CB_SIGNAL_DM = "cb_signal_dm"
CB_LIVE_MENU = "cb_live_menu"
CB_HOW_TO_ORDER = "cb_how_to_order"
CB_SUBMIT_ORDER = "cb_submit_order"
CB_PAY_BTC = "cb_pay_btc"
CB_PAY_ETH = "cb_pay_eth"
CB_PAY_USDT = "cb_pay_usdt"
CB_ABOUT = "cb_about"
CB_SUPPORT = "cb_support"
CB_BACK_TO_MAIN = "cb_back_to_main"

# Admin / Root
CB_ADMIN_MANAGEMENT = "admin_management"
CB_ADD_ADMIN = "add_admin"
CB_REMOVE_ADMIN = "remove_admin"
CB_LIST_ADMINS = "list_admins"
CB_BACK = "back"

# Payment method selection in order flow
PM_BTC = "PM_BTC"
PM_ETH = "PM_ETH"
PM_USDT = "PM_USDT"

# =========================
# CONVERSATION STATES
# =========================

# Order submission
STATE_ORDER_TEXT = 100
STATE_PAYMENT_METHOD = 101
STATE_RECEIVER_NAME = 102
STATE_ADDRESS = 103
STATE_CARRIER = 104
# =========================
# CONVERSATION STATES
# =========================

# Order submission
STATE_ORDER_TEXT = 100
STATE_PAYMENT_METHOD = 101
STATE_RECEIVER_NAME = 102
STATE_ADDRESS = 103
STATE_CARRIER = 104

# 🔑 Shared payment step (NEW)
STATE_PAYMENT_ORDER_ID = 190

# BTC payment
STATE_BTC_SUBTOTAL = 200
STATE_BTC_TXID = 201

# ETH payment
STATE_ETH_SUBTOTAL = 210
STATE_ETH_TXID = 211

# USDT payment
STATE_USDT_SUBTOTAL = 220
STATE_USDT_TXID = 221


# BTC payment
STATE_BTC_SUBTOTAL = 200
STATE_BTC_TXID = 201

# ETH payment
STATE_ETH_SUBTOTAL = 210
STATE_ETH_TXID = 211

# USDT payment
STATE_USDT_SUBTOTAL = 220
STATE_USDT_TXID = 221

# Admin management
STATE_ADD_ADMIN_ID = 1
STATE_REMOVE_ADMIN_SELECT = 2

# =========================
# PAYMENT METHOD DISPLAY NAMES
# =========================
PAYMENT_METHOD_NAMES = {
    "BTC": "₿ Bitcoin",
    "ETH": "Ξ Ethereum",
    "USDT": "💎 USDT (BEP20)"
}