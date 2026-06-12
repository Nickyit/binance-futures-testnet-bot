"""
Input Validation Module.

Provides comprehensive validation for all CLI inputs before they
are forwarded to the Binance API. Raises ``ValueError`` with
descriptive messages on any constraint violation.
"""

import logging
from typing import Optional

logger = logging.getLogger("trading_bot.validators")

# ---------------------------------------------------------------------------
# Allowed values
# ---------------------------------------------------------------------------
VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT")


class ValidationError(ValueError):
    """Custom exception for input validation failures."""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validate trading pair symbol.

    Parameters
    ----------
    symbol : str
        The futures trading pair, e.g. ``BTCUSDT``.

    Returns
    -------
    str
        Upper-cased, stripped symbol.

    Raises
    ------
    ValidationError
        If the symbol is empty or contains whitespace only.
    """
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol cannot be empty.")

    cleaned = symbol.strip().upper()
    logger.debug("Symbol validated: %s", cleaned)
    return cleaned


def validate_side(side: str) -> str:
    """
    Validate order side (BUY / SELL).

    Parameters
    ----------
    side : str
        Order side string.

    Returns
    -------
    str
        Normalised side (upper-case).

    Raises
    ------
    ValidationError
        If ``side`` is not ``BUY`` or ``SELL``.
    """
    normalised = side.strip().upper()
    if normalised not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of {VALID_SIDES}."
        )
    logger.debug("Side validated: %s", normalised)
    return normalised


def validate_order_type(order_type: str) -> str:
    """
    Validate order type (MARKET / LIMIT).

    Parameters
    ----------
    order_type : str
        Order type string.

    Returns
    -------
    str
        Normalised order type (upper-case).

    Raises
    ------
    ValidationError
        If ``order_type`` is not ``MARKET`` or ``LIMIT``.
    """
    normalised = order_type.strip().upper()
    if normalised not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {VALID_ORDER_TYPES}."
        )
    logger.debug("Order type validated: %s", normalised)
    return normalised


def validate_quantity(quantity: float) -> float:
    """
    Validate order quantity.

    Parameters
    ----------
    quantity : float
        Desired trade quantity.

    Returns
    -------
    float
        The validated quantity.

    Raises
    ------
    ValidationError
        If ``quantity`` is not a positive number.
    """
    try:
        qty = float(quantity)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            f"Quantity must be a valid number. Got: '{quantity}'."
        ) from exc

    if qty <= 0:
        raise ValidationError(
            f"Quantity must be greater than 0. Got: {qty}."
        )
    logger.debug("Quantity validated: %s", qty)
    return qty


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """
    Validate the price field.

    Price is **required** for ``LIMIT`` orders and **ignored** for
    ``MARKET`` orders.

    Parameters
    ----------
    price : float or None
        Limit price.
    order_type : str
        Already-validated order type.

    Returns
    -------
    float or None
        The validated price, or ``None`` for market orders.

    Raises
    ------
    ValidationError
        If ``order_type`` is ``LIMIT`` and ``price`` is missing or ≤ 0.
    """
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError(
                "Price is required for LIMIT orders. Use --price to specify."
            )
        try:
            p = float(price)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                f"Price must be a valid number. Got: '{price}'."
            ) from exc

        if p <= 0:
            raise ValidationError(
                f"Price must be greater than 0. Got: {p}."
            )
        logger.debug("Price validated: %s", p)
        return p

    # For MARKET orders, price is not required
    if price is not None:
        logger.info("Price argument ignored for MARKET orders.")
    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> dict:
    """
    Run all validators and return a clean parameter dict.

    Parameters
    ----------
    symbol : str
    side : str
    order_type : str
    quantity : float
    price : float or None

    Returns
    -------
    dict
        Validated parameters ready for the order API.

    Raises
    ------
    ValidationError
        On any validation failure.
    """
    validated_type = validate_order_type(order_type)

    params = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validated_type,
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, validated_type),
    }

    logger.info("All inputs validated successfully: %s", params)
    return params
