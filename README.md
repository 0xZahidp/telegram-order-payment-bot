# 🤖 Telegram Order & Payment Management Bot

A **production-ready Telegram bot** that combines **manual order submission** and **crypto payment tracking** (BTC / ETH / USDT) using **Google Sheets as a lightweight backend database**.

Built for Telegram-based storefronts where:
- Orders are reviewed manually
- Payments are verified by admins
- No traditional database is required

---

## ✨ Key Features

- 📝 Guided **order submission flow**
- 🆔 Auto-generated **Order IDs**
- 💳 Manual crypto payment handling:
  - Bitcoin (BTC)
  - Ethereum (ETH)
  - USDT
- 📦 Inventory-based pricing (from Google Sheets)
- 📊 Google Sheets used as:
  - Inventory DB
  - Order DB
  - Admin RBAC
  - Payment ledger
- 🛂 Admin & Root Admin role system
- 🔔 Admin notifications on new orders & payments
- 📋 Live menu display from Sheets
- 🧠 Safe conversation handling (no lost Order IDs)
- 🔐 No private keys stored anywhere

---

## 📸 Screenshots

> Below are real screenshots from the Telegram bot showing the order submission and crypto payment flows.  
> ⚠️ All screenshots use demo data. No real user or wallet information is exposed.

### 🤖 Bot – Start & Main Menu
<p align="center">
  <img 
    src="https://i.ibb.co.com/zhrjCkjq/Start-Main-Menu.png"
    width="380"
    alt="Telegram Bot Start and Main Menu"
  />
</p>
---

### 🧭 Core User Flows

<table align="center">
  <tr>
    <th align="center">📝 Order Submission Flow</th>
    <th align="center">💳 Crypto Payment Flow</th>
  </tr>
  <tr>
    <td align="center">
      <img 
        src="https://i.ibb.co.com/3Y98bQHp/Order-Submission-Flow.png"
        width="360"
        alt="Telegram Bot Order Submission Flow"
      />
    </td>
    <td align="center">
      <img 
        src="https://i.ibb.co.com/HD0mZmGh/Crypto-Payment-Flow.png"
        width="360"
        alt="Telegram Bot Crypto Payment Flow"
      />
    </td>
  </tr>
</table>
---

## 🧱 System Architecture

```

Telegram User
↓
Telegram Bot (python-telegram-bot v20+)
↓
Service Layer
├── OrderService
├── AdminService
├── MenuService
├── Payment Services
↓
Google Sheets (Database)
├── Inventory_List
├── Orders
├── Settings
├── Admins
├── BTC_Payments
├── ETH_Payments
└── USDT_Payments

```

---

## 🛠 Tech Stack

- Python 3.9+
- python-telegram-bot v20+
- Google Sheets API
- gspread
- OAuth2 Service Account
- python-dotenv

---

## 📂 Google Sheets Structure (Required)

Create **one Google Spreadsheet** with the following worksheets.

---

### 1️⃣ Inventory_List

Used to calculate prices and show menu items.

| Item Name | Category | Price Base | Quantity |
|----------|----------|------------|----------|
| LEMON BISCOTTI | BIGS | 450 | 15 |

- `Category`: BIGS / SMALLS
- `Price Base`: Base USD price
- `Quantity`: Available stock

---

### 2️⃣ Settings

Global configuration loaded dynamically by the bot.

| key | value |
|----|------|
| MARKUP_USD | 275 |
| BTC_FEE_PERCENT | 3 |
| ETH_FEE_PERCENT | 3 |
| USDT_FEE_PERCENT | 3 |
| BTC_WALLET | bc1q... |
| ETH_WALLET | 0x... |
| USDT_WALLET | 0x... |
| CURRENCY | $ |

⚠️ Changes here apply instantly without restarting the bot.

---

### 3️⃣ Orders

Stores all submitted orders.

| Order ID | Telegram Username | Order Text | Payment Method | Receiver Name | Address | Carrier | Status | Timestamp |

- `Status`: Pending Payment / Paid / Shipped / Cancelled

---

### 4️⃣ Admins

Role-based access control (RBAC).

| Telegram ID | Username | Type | Status | Added At |
|------------|----------|------|--------|----------|
| 123456789 | @username | root | active | 2026-01-10 |

- `Type`: root / admin
- `Status`: active / inactive

---

### 5️⃣ BTC_Payments

| Order ID | Subtotal USD | BTC Fee USD | Total USD | BTC Wallet | TXID | Status | Timestamp |

---

### 6️⃣ ETH_Payments

| Order ID | Subtotal USD | ETH Fee USD | Total USD | ETH Wallet | TXID | Status | Timestamp |

---

### 7️⃣ USDT_Payments

| Order ID | Subtotal USD | USDT Fee USD | Total USD | USDT Wallet | TXID | Status | Timestamp |

- `Status`: Pending / Confirmed / Rejected

---

## 🔐 Google API Setup

1. Open **Google Cloud Console**
2. Enable **Google Sheets API**
3. Create a **Service Account**
4. Generate a JSON key
5. Download it as:

```

service_account.json

````

6. Share the Google Sheet with the service account email  
   (**Editor permission required**)

---

## 🤖 Telegram Bot Setup

1. Create a bot via **@BotFather**
2. Copy the bot token
3. Add the bot to Telegram
4. Add your Telegram ID to the `Admins` sheet as `root`
5. Start the bot using `/start`

---

## ⚙️ Environment Configuration

Create a `.env` file:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_telegram_id
GOOGLE_SHEET_ID=your_google_sheet_id
SERVICE_ACCOUNT_JSON_PATH=service_account.json
````

⚠️ Never commit `.env` or credential files.

---

## ▶️ Running the Bot

```bash
python main.py
```

Expected output:

```
🤖 Bot is running...
```

---

## 🧪 User Flow

1. User runs `/start`
2. Opens **Live Menu**
3. Submits an order
4. Selects payment method
5. Receives Order ID
6. Makes crypto payment
7. Admin verifies payment
8. Order status updated in Sheets

---

## 🔒 Security Notes

* `.env` and credentials are ignored via `.gitignore`
* Payments are manually verified
* No blockchain private keys stored
* Admin access fully controlled via Sheets

---

## 🚀 Production Deployment Tips

* Use **systemd** on VPS to keep bot alive
* Restrict Google Sheet access
* Use private repo for client deployments
* Rotate bot token periodically

---

## 📌 Project Status

* ✅ Stable
* ✅ Production-ready
* ✅ Client-tested
* ✅ Easily extendable

---

## 📜 License

MIT License

---

## ⭐ Support

If this project helps you:

* ⭐ Star the repository
* 🍴 Fork it
* 🛠 Submit improvements