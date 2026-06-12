# Binance Futures Testnet Trading Bot

A production-quality Python CLI trading bot for placing **MARKET** and **LIMIT** orders on the **Binance Futures Testnet (USDT-M)**.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Testnet Setup & API Keys](#testnet-setup--api-keys)
- [Configuration](#configuration)
- [Usage](#usage)
  - [MARKET Order Examples](#market-order-examples)
  - [LIMIT Order Examples](#limit-order-examples)
- [CLI Arguments](#cli-arguments)
- [Input Validation](#input-validation)
- [Logging](#logging)
- [Error Handling](#error-handling)
- [License](#license)

---

## Features

| Feature | Description |
|---|---|
| **Testnet Safe** | All orders go to the Binance Futures **Testnet** — no real funds at risk |
| **MARKET Orders** | Instant execution at the best available price |
| **LIMIT Orders** | Place orders at a specific price (GTC — Good Till Cancelled) |
| **BUY / SELL** | Full support for both order sides |
| **Input Validation** | Strict checks on symbol, side, type, quantity, and price |
| **Structured Logging** | Rotating file logs (`logs/bot.log`) + coloured console output |
| **Exception Handling** | Graceful handling of API errors, network failures, and bad input |
| **Rich CLI Output** | ASCII-formatted order summaries with status, fill info, and avg price |

---

## Project Structure

```
trading_bot/
│
├── bot/                      # Core bot package
│   ├── __init__.py           # Package metadata
│   ├── __main__.py           # Module entry point (python -m bot)
│   ├── client.py             # Binance Testnet client wrapper
│   ├── orders.py             # Order placement & formatting
│   ├── validators.py         # Input validation logic
│   └── logging_config.py     # Centralised logging setup
│
├── tests/                    # Unit tests
│   ├── __init__.py
│   └── test_validators.py    # 41 test cases for input validation
│
├── logs/                     # Auto-created log directory
│   └── bot.log               # Rotating log file
│
├── cli.py                    # CLI entry point (argparse)
├── .env.example              # Template for API credentials
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### Module Descriptions

| Module | Responsibility |
|---|---|
| `bot/client.py` | Loads credentials from `.env`, creates an authenticated `python-binance` client pointing at the Futures Testnet, and verifies connectivity |
| `bot/orders.py` | `OrderManager` class that builds order params, calls the Binance API, and formats request/response summaries |
| `bot/validators.py` | Pure validation functions for every CLI input; raises `ValidationError` on failure |
| `bot/logging_config.py` | Sets up a `RotatingFileHandler` (5 MB, 3 backups) and a console handler |
| `cli.py` | Parses CLI arguments, orchestrates the full workflow, and prints results |

---

## Prerequisites

- **Python 3.8+** (tested on 3.13)
- **pip** (Python package manager)
- A **Binance Futures Testnet** account with API credentials

---

## Installation

```bash
# 1. Clone or download the project
git clone https://github.com/Nickyit/binance-futures-testnet-bot.git
cd binance-futures-testnet-bot

# 2. (Recommended) Create a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

That's it — the project is **runnable immediately** after `pip install -r requirements.txt`.

---

## Testnet Setup & API Keys

### Step 1 — Create a Testnet Account

1. Go to the **Binance Futures Testnet**: [https://testnet.binancefuture.com/](https://testnet.binancefuture.com/)
2. Click **"Log In with GitHub"** and authorise with your GitHub account
3. Once logged in you will see a trading dashboard with **test USDT** already credited

### Step 2 — Generate API Keys

1. On the testnet dashboard, look for the **"API Key"** section (top-right menu or sidebar)
2. Click **"Generate HMAC_SHA256 Key"**
3. Copy both:
   - **API Key** (public key)
   - **Secret Key** (private key — shown only once!)
4. Save them securely

### Step 3 — Important Notes

> **These are TESTNET keys** — they only work on `testnet.binancefuture.com`, not on real Binance.
>
> If your keys expire or stop working, simply generate a new pair from the testnet dashboard.

---

## Configuration

```bash
# Copy the example env file
cp .env.example .env          # Linux / macOS
copy .env.example .env        # Windows

# Edit .env and paste your keys
API_KEY=your_testnet_api_key_here
API_SECRET=your_testnet_api_secret_here
```

---

## Usage

### MARKET Order Examples

**Buy 0.01 BTC with a market order:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Sell 0.5 ETH with a market order:**
```bash
python cli.py --symbol ETHUSDT --side SELL --type MARKET --quantity 0.5
```

**Buy 100 DOGE with a market order:**
```bash
python cli.py --symbol DOGEUSDT --side BUY --type MARKET --quantity 100
```

### LIMIT Order Examples

**Buy 0.01 BTC at $60,000:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 60000
```

**Sell 1 ETH at $2,500:**
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 1 --price 2500
```

**Buy 50 SOL at $150:**
```bash
python cli.py --symbol SOLUSDT --side BUY --type LIMIT --quantity 50 --price 150
```

### Sample Output

```
+==================================================+
|            ORDER REQUEST SUMMARY                  |
+==================================================+
|  Symbol     : BTCUSDT                            |
|  Side       : BUY                                |
|  Type       : MARKET                             |
|  Quantity   : 0.01                               |
+==================================================+

[OK] Connected to Binance Futures Testnet successfully.

+==================================================+
|            ORDER RESPONSE DETAILS                 |
+==================================================+
|  Order ID       : 123456789                      |
|  Client ID      : abc123xyz                      |
|  Symbol         : BTCUSDT                        |
|  Side           : BUY                            |
|  Type           : MARKET                         |
|  Status         : FILLED                         |
|  Orig Quantity  : 0.01                           |
|  Executed Qty   : 0.01                           |
|  Price          : 0                              |
|  Avg Price      : 68452.30                       |
|  Update Time    : 1718234567890                  |
+==================================================+

[SUCCESS] Order 123456789 placed with status: FILLED
```

---

## CLI Arguments

| Argument | Required | Description |
|---|---|---|
| `--symbol` | ✅ | Futures trading pair (e.g. `BTCUSDT`, `ETHUSDT`) |
| `--side` | ✅ | Order side: `BUY` or `SELL` |
| `--type` | ✅ | Order type: `MARKET` or `LIMIT` |
| `--quantity` | ✅ | Trade quantity (must be `> 0`) |
| `--price` | 🔶 | Limit price (**required for LIMIT orders only**) |

---

## Input Validation

The bot validates every input **before** contacting the API:

| Field | Rule |
|---|---|
| `symbol` | Cannot be empty or whitespace |
| `side` | Must be `BUY` or `SELL` (case-insensitive) |
| `type` | Must be `MARKET` or `LIMIT` (case-insensitive) |
| `quantity` | Must be a number greater than `0` |
| `price` | Required and `> 0` for `LIMIT` orders; ignored for `MARKET` |

If validation fails, the bot prints a clear error and exits **without** making any API call.

---

## Logging

All activity is logged to **`logs/bot.log`** with automatic rotation:

- **File handler**: `DEBUG` level and above (captures everything)
- **Console handler**: `INFO` level and above (clean terminal output)
- **Rotation**: 5 MB per file, 3 backup files retained

Logged events include:
- All API request parameters
- Full API responses
- Validation outcomes
- Errors and stack traces

---

## Error Handling

| Error Category | Handling |
|---|---|
| **Invalid Input** | `ValidationError` with descriptive message; exits before API call |
| **Missing `.env`** | `EnvironmentError` with setup instructions |
| **Binance API Error** | `BinanceAPIException` — logs status code + message |
| **Network Error** | `BinanceRequestException` / `ConnectionError` — logged with details |
| **Unexpected Error** | Caught by global `except`, full traceback logged to file |

---

## Testing

Run the unit test suite (41 test cases covering all validators):

```bash
python -m unittest tests.test_validators -v
```

---

## License

This project is provided for **educational and testing purposes only**.
Use at your own risk. Not intended for real-money trading.
