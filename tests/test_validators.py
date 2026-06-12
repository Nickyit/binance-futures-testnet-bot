"""
Unit Tests for the Validators Module.

Tests cover all validation functions including edge cases
for symbol, side, order type, quantity, and price validators.

Run with:
    python -m pytest tests/ -v
    or
    python -m unittest tests.test_validators -v
"""

import unittest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_all,
    ValidationError,
)


class TestValidateSymbol(unittest.TestCase):
    """Tests for validate_symbol()."""

    def test_valid_symbol(self):
        self.assertEqual(validate_symbol("BTCUSDT"), "BTCUSDT")

    def test_lowercase_symbol(self):
        self.assertEqual(validate_symbol("btcusdt"), "BTCUSDT")

    def test_mixed_case_symbol(self):
        self.assertEqual(validate_symbol("BtcUsdt"), "BTCUSDT")

    def test_symbol_with_whitespace(self):
        self.assertEqual(validate_symbol("  ETHUSDT  "), "ETHUSDT")

    def test_empty_symbol_raises(self):
        with self.assertRaises(ValidationError):
            validate_symbol("")

    def test_whitespace_only_symbol_raises(self):
        with self.assertRaises(ValidationError):
            validate_symbol("   ")

    def test_none_symbol_raises(self):
        with self.assertRaises(ValidationError):
            validate_symbol(None)


class TestValidateSide(unittest.TestCase):
    """Tests for validate_side()."""

    def test_buy_uppercase(self):
        self.assertEqual(validate_side("BUY"), "BUY")

    def test_sell_uppercase(self):
        self.assertEqual(validate_side("SELL"), "SELL")

    def test_buy_lowercase(self):
        self.assertEqual(validate_side("buy"), "BUY")

    def test_sell_lowercase(self):
        self.assertEqual(validate_side("sell"), "SELL")

    def test_buy_with_whitespace(self):
        self.assertEqual(validate_side("  BUY  "), "BUY")

    def test_invalid_side_raises(self):
        with self.assertRaises(ValidationError):
            validate_side("HOLD")

    def test_empty_side_raises(self):
        with self.assertRaises(ValidationError):
            validate_side("")


class TestValidateOrderType(unittest.TestCase):
    """Tests for validate_order_type()."""

    def test_market_uppercase(self):
        self.assertEqual(validate_order_type("MARKET"), "MARKET")

    def test_limit_uppercase(self):
        self.assertEqual(validate_order_type("LIMIT"), "LIMIT")

    def test_market_lowercase(self):
        self.assertEqual(validate_order_type("market"), "MARKET")

    def test_limit_lowercase(self):
        self.assertEqual(validate_order_type("limit"), "LIMIT")

    def test_invalid_type_raises(self):
        with self.assertRaises(ValidationError):
            validate_order_type("STOP")

    def test_empty_type_raises(self):
        with self.assertRaises(ValidationError):
            validate_order_type("")


class TestValidateQuantity(unittest.TestCase):
    """Tests for validate_quantity()."""

    def test_valid_integer_quantity(self):
        self.assertEqual(validate_quantity(1), 1.0)

    def test_valid_float_quantity(self):
        self.assertEqual(validate_quantity(0.01), 0.01)

    def test_valid_string_number(self):
        self.assertEqual(validate_quantity("0.5"), 0.5)

    def test_zero_quantity_raises(self):
        with self.assertRaises(ValidationError):
            validate_quantity(0)

    def test_negative_quantity_raises(self):
        with self.assertRaises(ValidationError):
            validate_quantity(-1.5)

    def test_non_numeric_string_raises(self):
        with self.assertRaises(ValidationError):
            validate_quantity("abc")

    def test_none_quantity_raises(self):
        with self.assertRaises(ValidationError):
            validate_quantity(None)


class TestValidatePrice(unittest.TestCase):
    """Tests for validate_price()."""

    def test_limit_order_with_valid_price(self):
        self.assertEqual(validate_price(50000.0, "LIMIT"), 50000.0)

    def test_limit_order_with_string_price(self):
        self.assertEqual(validate_price("2500", "LIMIT"), 2500.0)

    def test_limit_order_missing_price_raises(self):
        with self.assertRaises(ValidationError):
            validate_price(None, "LIMIT")

    def test_limit_order_zero_price_raises(self):
        with self.assertRaises(ValidationError):
            validate_price(0, "LIMIT")

    def test_limit_order_negative_price_raises(self):
        with self.assertRaises(ValidationError):
            validate_price(-100, "LIMIT")

    def test_market_order_price_ignored(self):
        self.assertIsNone(validate_price(50000, "MARKET"))

    def test_market_order_no_price(self):
        self.assertIsNone(validate_price(None, "MARKET"))


class TestValidateAll(unittest.TestCase):
    """Tests for validate_all() integration."""

    def test_valid_market_order(self):
        result = validate_all(
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.01,
        )
        self.assertEqual(result["symbol"], "BTCUSDT")
        self.assertEqual(result["side"], "BUY")
        self.assertEqual(result["order_type"], "MARKET")
        self.assertEqual(result["quantity"], 0.01)
        self.assertIsNone(result["price"])

    def test_valid_limit_order(self):
        result = validate_all(
            symbol="ETHUSDT",
            side="SELL",
            order_type="LIMIT",
            quantity=1.0,
            price=2500.0,
        )
        self.assertEqual(result["symbol"], "ETHUSDT")
        self.assertEqual(result["side"], "SELL")
        self.assertEqual(result["order_type"], "LIMIT")
        self.assertEqual(result["quantity"], 1.0)
        self.assertEqual(result["price"], 2500.0)

    def test_limit_order_without_price_raises(self):
        with self.assertRaises(ValidationError):
            validate_all(
                symbol="BTCUSDT",
                side="BUY",
                order_type="LIMIT",
                quantity=0.01,
            )

    def test_invalid_symbol_raises(self):
        with self.assertRaises(ValidationError):
            validate_all(
                symbol="",
                side="BUY",
                order_type="MARKET",
                quantity=0.01,
            )

    def test_invalid_side_raises(self):
        with self.assertRaises(ValidationError):
            validate_all(
                symbol="BTCUSDT",
                side="HOLD",
                order_type="MARKET",
                quantity=0.01,
            )

    def test_invalid_quantity_raises(self):
        with self.assertRaises(ValidationError):
            validate_all(
                symbol="BTCUSDT",
                side="BUY",
                order_type="MARKET",
                quantity=-5,
            )

    def test_case_insensitive_inputs(self):
        """Verify that lowercase inputs are normalised correctly."""
        result = validate_all(
            symbol="btcusdt",
            side="buy",
            order_type="market",
            quantity=0.01,
        )
        self.assertEqual(result["symbol"], "BTCUSDT")
        self.assertEqual(result["side"], "BUY")
        self.assertEqual(result["order_type"], "MARKET")


if __name__ == "__main__":
    unittest.main()
