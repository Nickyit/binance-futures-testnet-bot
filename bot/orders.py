"""
Order Execution Module.

Provides the ``OrderManager`` class that handles building, placing,
and reporting on MARKET and LIMIT orders via the Binance Futures
Testnet API.
"""

import logging
from typing import Optional

from binance.client import Client
from binance.enums import (
    SIDE_BUY,
    SIDE_SELL,
    ORDER_TYPE_MARKET,
    ORDER_TYPE_LIMIT,
    TIME_IN_FORCE_GTC,
)
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger("trading_bot.orders")


class OrderManager:
    """
    Manages order creation and result formatting for Binance
    Futures Testnet.

    Parameters
    ----------
    client : binance.client.Client
        An authenticated Binance client instance (testnet).
    """

    # Map user-friendly strings -> binance-python constants
    SIDE_MAP = {
        "BUY": SIDE_BUY,
        "SELL": SIDE_SELL,
    }
    TYPE_MAP = {
        "MARKET": ORDER_TYPE_MARKET,
        "LIMIT": ORDER_TYPE_LIMIT,
    }

    def __init__(self, client: Client) -> None:
        self.client = client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> dict:
        """
        Place a MARKET or LIMIT order on Binance Futures Testnet.

        Parameters
        ----------
        symbol : str
            Trading pair, e.g. ``BTCUSDT``.
        side : str
            ``BUY`` or ``SELL``.
        order_type : str
            ``MARKET`` or ``LIMIT``.
        quantity : float
            Order quantity.
        price : float or None
            Limit price (required for LIMIT orders).

        Returns
        -------
        dict
            Raw API response from Binance.

        Raises
        ------
        BinanceAPIException
            On any Binance server-side error.
        BinanceRequestException
            On network-level errors.
        ConnectionError
            On general connectivity issues.
        """
        # Build the base order parameters
        params = {
            "symbol": symbol,
            "side": self.SIDE_MAP[side],
            "type": self.TYPE_MAP[order_type],
            "quantity": quantity,
        }

        # LIMIT orders require price and timeInForce
        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = TIME_IN_FORCE_GTC

        logger.info("Placing %s %s order: %s", side, order_type, params)

        try:
            response = self.client.futures_create_order(**params)
            logger.info("Order placed successfully. Response: %s", response)
            return response

        except BinanceAPIException as exc:
            logger.error(
                "Binance API error [%s]: %s", exc.status_code, exc.message
            )
            raise
        except BinanceRequestException as exc:
            logger.error("Binance request error: %s", exc)
            raise
        except ConnectionError as exc:
            logger.error("Network connection error: %s", exc)
            raise

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def format_order_request(
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float],
    ) -> str:
        """
        Build a human-readable summary of the order *request*.

        Returns
        -------
        str
            Multi-line request summary.
        """
        lines = [
            "",
            "+==================================================+",
            "|            ORDER REQUEST SUMMARY                  |",
            "+==================================================+",
            f"|  Symbol     : {symbol:<35}|",
            f"|  Side       : {side:<35}|",
            f"|  Type       : {order_type:<35}|",
            f"|  Quantity   : {str(quantity):<35}|",
        ]
        if price is not None:
            lines.append(f"|  Price      : {str(price):<35}|")
        lines.append("+==================================================+")
        return "\n".join(lines)

    @staticmethod
    def format_order_response(response: dict) -> str:
        """
        Build a human-readable summary of the order *response*.

        Parameters
        ----------
        response : dict
            Raw Binance API order response.

        Returns
        -------
        str
            Multi-line response summary.
        """
        order_id = response.get("orderId", "N/A")
        status = response.get("status", "N/A")
        executed_qty = response.get("executedQty", "N/A")
        avg_price = response.get("avgPrice", "N/A")
        client_order_id = response.get("clientOrderId", "N/A")
        order_type = response.get("type", "N/A")
        side = response.get("side", "N/A")
        symbol = response.get("symbol", "N/A")
        orig_qty = response.get("origQty", "N/A")
        price = response.get("price", "N/A")
        update_time = response.get("updateTime", "N/A")

        lines = [
            "",
            "+==================================================+",
            "|            ORDER RESPONSE DETAILS                 |",
            "+==================================================+",
            f"|  Order ID       : {str(order_id):<31}|",
            f"|  Client ID      : {str(client_order_id):<31}|",
            f"|  Symbol         : {str(symbol):<31}|",
            f"|  Side           : {str(side):<31}|",
            f"|  Type           : {str(order_type):<31}|",
            f"|  Status         : {str(status):<31}|",
            f"|  Orig Quantity  : {str(orig_qty):<31}|",
            f"|  Executed Qty   : {str(executed_qty):<31}|",
            f"|  Price          : {str(price):<31}|",
            f"|  Avg Price      : {str(avg_price):<31}|",
            f"|  Update Time    : {str(update_time):<31}|",
            "+==================================================+",
        ]
        return "\n".join(lines)
