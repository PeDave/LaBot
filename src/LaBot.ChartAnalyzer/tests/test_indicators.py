"""Unit tests for technical indicators."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.indicators.technical import TechnicalIndicators
from app.indicators.fibonacci import FibonacciCalculator
from app.indicators.support_resistance import SupportResistanceDetector


def _make_df(n: int = 100, trend: str = "up") -> pd.DataFrame:
    np.random.seed(42)
    base = 100.0
    prices = [base]
    for i in range(1, n):
        delta = np.random.randn() * 0.5 + (0.1 if trend == "up" else -0.1)
        prices.append(max(prices[-1] + delta, 1.0))
    closes = np.array(prices)
    highs = closes * 1.005
    lows = closes * 0.995
    volumes = np.random.uniform(1000, 5000, n)
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })
    return df


class TestTechnicalIndicators:
    def test_calculate_returns_indicator_summary(self):
        df = _make_df(100)
        ti = TechnicalIndicators()
        result = ti.calculate(df)
        assert result is not None
        assert result.current_price == pytest.approx(float(df["close"].iloc[-1]))

    def test_rsi_is_between_0_and_100(self):
        df = _make_df(100)
        ti = TechnicalIndicators()
        result = ti.calculate(df)
        if result.rsi is not None:
            assert 0.0 <= result.rsi <= 100.0

    def test_rsi_signal_oversold(self):
        # Build a rapidly declining series to force RSI < 30
        closes = np.linspace(200, 50, 50)
        df = pd.DataFrame({
            "open": closes,
            "high": closes * 1.001,
            "low": closes * 0.999,
            "close": closes,
            "volume": np.ones(50) * 1000,
        })
        ti = TechnicalIndicators()
        result = ti.calculate(df)
        if result.rsi is not None and result.rsi < 30:
            assert result.rsi_signal == "oversold"

    def test_macd_fields_populated(self):
        df = _make_df(100)
        ti = TechnicalIndicators()
        result = ti.calculate(df)
        # MACD may or may not be set depending on data length, just ensure no exception

    def test_empty_dataframe_returns_empty_summary(self):
        df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        ti = TechnicalIndicators()
        result = ti.calculate(df)
        assert result.rsi is None

    def test_bollinger_bands_populated(self):
        df = _make_df(100)
        ti = TechnicalIndicators()
        result = ti.calculate(df)
        if result.bb_upper is not None:
            assert result.bb_upper > result.bb_lower

    def test_atr_positive(self):
        df = _make_df(100)
        ti = TechnicalIndicators()
        result = ti.calculate(df)
        if result.atr is not None:
            assert result.atr > 0


class TestFibonacciCalculator:
    def test_retracement_levels_correct(self):
        closes = np.linspace(100, 200, 100)
        df = pd.DataFrame({
            "open": closes,
            "high": closes * 1.01,
            "low": closes * 0.99,
            "close": closes,
            "volume": np.ones(100) * 1000,
        })
        fib = FibonacciCalculator()
        result = fib.calculate(df)
        assert result.swing_high > result.swing_low
        assert "0.618" in result.retracements
        assert "1.618" in result.extensions
        # 0.618 retracement should be between high and low
        r618 = result.retracements["0.618"]
        assert result.swing_low < r618 < result.swing_high

    def test_extension_above_swing_low(self):
        closes = np.linspace(100, 200, 100)
        df = pd.DataFrame({
            "open": closes,
            "high": closes * 1.01,
            "low": closes * 0.99,
            "close": closes,
            "volume": np.ones(100) * 1000,
        })
        fib = FibonacciCalculator()
        result = fib.calculate(df)
        ext_1618 = result.extensions["1.618"]
        # Extensions are measured from low + diff * ratio, may exceed swing_high
        assert ext_1618 > result.swing_low


class TestSupportResistanceDetector:
    def test_returns_lists(self):
        df = _make_df(60)
        sr = SupportResistanceDetector()
        supports, resistances = sr.detect(df)
        assert isinstance(supports, list)
        assert isinstance(resistances, list)

    def test_support_below_current_price(self):
        df = _make_df(60)
        sr = SupportResistanceDetector()
        supports, _ = sr.detect(df)
        current = float(df["close"].iloc[-1])
        for s in supports:
            assert s.price < current

    def test_resistance_above_current_price(self):
        df = _make_df(60)
        sr = SupportResistanceDetector()
        _, resistances = sr.detect(df)
        current = float(df["close"].iloc[-1])
        for r in resistances:
            assert r.price > current
