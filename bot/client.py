"""
Binance Futures Testnet Client Module.

Encapsulates all interaction with the Binance Futures Testnet API
via the ``python-binance`` library. Handles client initialisation,
credential loading, and connection verification.
"""

import logging
import os

from dotenv import load_dotenv
from binance.client import Client, BaseClient
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger("trading_bot.client")

# ---------------------------------------------------------------------------
# Binance Futures Testnet endpoints
# ---------------------------------------------------------------------------
# python-binance v1.0.37: testnet=True does NOT override FUTURES_URL.
# It only changes WebSocket URLs. We must set FUTURES_URL explicitly.
FUTURES_TESTNET_URL = BaseClient.FUTURES_TESTNET_URL  # https://testnet.binancefuture.com/fapi


class BinanceTestnetClient:
    """
    Wrapper around ``binance.client.Client`` configured for the
    Binance Futures USDT-M Testnet.

    Attributes
    ----------
    client : binance.client.Client
        Authenticated Binance client instance.

    Usage
    -----
    >>> tc = BinanceTestnetClient()
    >>> tc.verify_connection()
    True
    """

    def __init__(self) -> None:
        """
        Initialise the client by loading API credentials from ``.env``
        and pointing at the Futures Testnet endpoint.

        Raises
        ------
        EnvironmentError
            If ``API_KEY`` or ``API_SECRET`` are not set.
        BinanceAPIException
            If the Binance API rejects the credentials.
        """
        # Load environment variables from .env file
        load_dotenv()

        api_key = os.getenv("API_KEY")
        api_secret = os.getenv("API_SECRET")

        if not api_key or not api_secret:
            logger.error("API_KEY and/or API_SECRET not found in environment.")
            raise EnvironmentError(
                "API_KEY and API_SECRET must be set in the .env file. "
                "See .env.example for reference."
            )

        logger.debug("API credentials loaded from environment.")

        # Build the client with testnet=True (handles WS URLs)
        # then explicitly override FUTURES_URL for REST API calls
        self.client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True,
        )

        # CRITICAL: testnet=True does NOT change FUTURES_URL in v1.0.37.
        # Without this override, futures_create_order() hits PRODUCTION
        # Binance (fapi.binance.com) and fails with invalid credentials.
        self.client.FUTURES_URL = FUTURES_TESTNET_URL

        logger.info(
            "Binance Futures Testnet client initialised. FUTURES_URL=%s",
            self.client.FUTURES_URL,
        )

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def verify_connection(self) -> bool:
        """
        Ping the Binance Futures Testnet and fetch server time to
        ensure the connection is live and credentials are valid.

        Returns
        -------
        bool
            ``True`` if the server responds successfully.

        Raises
        ------
        BinanceAPIException
            On authentication or server-side failure.
        BinanceRequestException
            On network-level failure.
        """
        try:
            server_time = self.client.futures_time()
            logger.info(
                "Connection verified - server time: %s",
                server_time.get("serverTime"),
            )
            return True
        except BinanceAPIException as exc:
            logger.error("API error during connection check: %s", exc)
            raise
        except BinanceRequestException as exc:
            logger.error("Network error during connection check: %s", exc)
            raise

    def get_account_info(self) -> dict:
        """
        Retrieve Futures Testnet account information.

        Returns
        -------
        dict
            Account details including balances and positions.
        """
        try:
            info = self.client.futures_account()
            logger.debug("Account info retrieved successfully.")
            return info
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Failed to fetch account info: %s", exc)
            raise

    def get_client(self) -> Client:
        """Return the underlying ``binance.client.Client`` instance."""
        return self.client
