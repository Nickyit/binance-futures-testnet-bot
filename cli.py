#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot – CLI Entry Point.

Usage examples
--------------
Market order:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

Limit order:
    python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.5 --price 2500
"""

import argparse
import io
import sys

from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.logging_config import setup_logging
from bot.validators import validate_all, ValidationError
from bot.client import BinanceTestnetClient
from bot.orders import OrderManager

# ---------------------------------------------------------------------------
# Force UTF-8 output on Windows so emoji / box-drawing chars render properly
# ---------------------------------------------------------------------------
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )

# ---------------------------------------------------------------------------
# Initialise application-wide logger
# ---------------------------------------------------------------------------
logger = setup_logging()


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """
    Construct the ``argparse.ArgumentParser`` with all required
    and optional CLI arguments.

    Returns
    -------
    argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description=(
            "Binance Futures Testnet Trading Bot -- "
            "Place MARKET and LIMIT orders via the CLI."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.01\n"
            "  python cli.py --symbol ETHUSDT --side SELL --type LIMIT  --quantity 0.5 --price 2500\n"
        ),
    )

    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Futures trading pair symbol (e.g. BTCUSDT, ETHUSDT).",
    )
    parser.add_argument(
        "--side",
        type=str,
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side: BUY or SELL.",
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type: MARKET or LIMIT.",
    )
    parser.add_argument(
        "--quantity",
        type=float,
        required=True,
        help="Order quantity (must be > 0).",
    )
    parser.add_argument(
        "--price",
        type=float,
        required=False,
        default=None,
        help="Limit price (required for LIMIT orders).",
    )

    return parser


# ---------------------------------------------------------------------------
# Main execution flow
# ---------------------------------------------------------------------------
def main() -> None:
    """
    Entry point for the trading bot CLI.

    Workflow:
        1. Parse CLI arguments.
        2. Validate all inputs.
        3. Initialise the Binance Testnet client.
        4. Place the order.
        5. Display results.
    """
    parser = build_parser()
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Binance Futures Testnet Trading Bot started")
    logger.info("=" * 60)

    # -- Step 1: Validate inputs ------------------------------------------
    try:
        params = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as exc:
        logger.error("Input validation failed: %s", exc)
        print(f"\n[ERROR] Validation Error: {exc}")
        sys.exit(1)

    # -- Step 2: Display order request summary ----------------------------
    request_summary = OrderManager.format_order_request(
        symbol=params["symbol"],
        side=params["side"],
        order_type=params["order_type"],
        quantity=params["quantity"],
        price=params["price"],
    )
    print(request_summary)
    logger.info("Order request summary displayed.")

    # -- Step 3: Initialise Binance Testnet client ------------------------
    try:
        testnet_client = BinanceTestnetClient()
        testnet_client.verify_connection()
        print("\n[OK] Connected to Binance Futures Testnet successfully.")
    except EnvironmentError as exc:
        logger.error("Environment setup error: %s", exc)
        print(f"\n[ERROR] Configuration Error: {exc}")
        sys.exit(1)
    except BinanceAPIException as exc:
        logger.error("API authentication failed: %s", exc)
        print(f"\n[ERROR] API Error ({exc.status_code}): {exc.message}")
        sys.exit(1)
    except BinanceRequestException as exc:
        logger.error("Network error during initialisation: %s", exc)
        print(f"\n[ERROR] Network Error: {exc}")
        sys.exit(1)

    # -- Step 4: Place the order ------------------------------------------
    order_manager = OrderManager(testnet_client.get_client())

    try:
        response = order_manager.place_order(
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["order_type"],
            quantity=params["quantity"],
            price=params["price"],
        )
    except BinanceAPIException as exc:
        logger.error("Order failed - API error [%s]: %s", exc.status_code, exc.message)
        print(f"\n[ERROR] Order Failed (API Error {exc.status_code}): {exc.message}")
        sys.exit(1)
    except BinanceRequestException as exc:
        logger.error("Order failed - network error: %s", exc)
        print(f"\n[ERROR] Order Failed (Network Error): {exc}")
        sys.exit(1)
    except ConnectionError as exc:
        logger.error("Order failed - connection error: %s", exc)
        print(f"\n[ERROR] Order Failed (Connection Error): {exc}")
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error while placing order: %s", exc)
        print(f"\n[ERROR] Unexpected Error: {exc}")
        sys.exit(1)

    # -- Step 5: Display order response -----------------------------------
    response_summary = OrderManager.format_order_response(response)
    print(response_summary)

    status = response.get("status", "UNKNOWN")
    order_id = response.get("orderId", "N/A")

    if status in ("FILLED", "NEW", "PARTIALLY_FILLED"):
        print(f"\n[SUCCESS] Order {order_id} placed with status: {status}")
        logger.info("Order %s completed with status: %s", order_id, status)
    else:
        print(f"\n[WARNING] Order {order_id} returned status: {status}")
        logger.warning("Order %s returned unexpected status: %s", order_id, status)

    logger.info("Trading bot execution finished.\n")


# ---------------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
