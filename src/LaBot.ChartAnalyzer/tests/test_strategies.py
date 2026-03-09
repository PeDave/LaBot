"""Unit tests for trading strategy calculators."""
from __future__ import annotations

import pytest

from app.api.models import IndicatorSummary, PriceLevel
from app.strategies.entry_calculator import EntryCalculator
from app.strategies.stop_loss import StopLossCalculator
from app.strategies.take_profit import TakeProfitCalculator
from app.strategies.risk_manager import RiskManager


class TestEntryCalculator:
    def test_breakout_entry_above_resistance(self):
        calc = EntryCalculator()
        indicators = IndicatorSummary(current_price=100.0)
        resistances = [PriceLevel(price=105.0, strength=0.8)]
        entry = calc.calculate_bullish_entry(indicators, resistances, [])
        assert entry is not None
        assert entry.type == "breakout"
        assert entry.price > 105.0

    def test_reversal_entry_when_oversold(self):
        calc = EntryCalculator()
        indicators = IndicatorSummary(current_price=100.0, rsi=25.0, rsi_signal="oversold")
        entry = calc.calculate_bullish_entry(indicators, [], [])
        assert entry is not None
        assert entry.type == "reversal"

    def test_bearish_entry_below_support(self):
        calc = EntryCalculator()
        indicators = IndicatorSummary(current_price=100.0)
        supports = [PriceLevel(price=95.0, strength=0.7)]
        entry = calc.calculate_bearish_entry(indicators, [], supports)
        assert entry is not None
        assert entry.type == "breakdown"
        assert entry.price < 95.0

    def test_returns_none_without_price(self):
        calc = EntryCalculator()
        entry = calc.calculate_bullish_entry(IndicatorSummary(), [], [])
        assert entry is None


class TestStopLossCalculator:
    def test_long_sl_below_entry(self):
        sl_calc = StopLossCalculator()
        indicators = IndicatorSummary(atr=2.0)
        sl = sl_calc.calculate_long_sl(100.0, indicators, [])
        assert sl < 100.0

    def test_short_sl_above_entry(self):
        sl_calc = StopLossCalculator()
        indicators = IndicatorSummary(atr=2.0)
        sl = sl_calc.calculate_short_sl(100.0, indicators, [])
        assert sl > 100.0

    def test_long_sl_with_support_level(self):
        sl_calc = StopLossCalculator()
        indicators = IndicatorSummary(atr=None)
        supports = [PriceLevel(price=90.0, strength=0.9)]
        sl = sl_calc.calculate_long_sl(100.0, indicators, supports)
        assert sl < 100.0
        assert sl < 91.0

    def test_percentage_fallback(self):
        sl_calc = StopLossCalculator()
        indicators = IndicatorSummary()
        sl = sl_calc.calculate_long_sl(100.0, indicators, [], percentage=0.03)
        assert sl == pytest.approx(97.0)


class TestTakeProfitCalculator:
    def test_tp_levels_ascending(self):
        tp_calc = TakeProfitCalculator()
        tp1, tp2, tp3 = tp_calc.calculate_long_tps(100.0, 95.0)
        assert tp1 < tp2 < tp3

    def test_tp1_is_1r_risk(self):
        tp_calc = TakeProfitCalculator()
        tp1, tp2, tp3 = tp_calc.calculate_long_tps(100.0, 95.0)
        assert tp1 == pytest.approx(105.0)
        assert tp2 == pytest.approx(110.0)
        assert tp3 == pytest.approx(115.0)

    def test_short_tp_levels_descending(self):
        tp_calc = TakeProfitCalculator()
        tp1, tp2, tp3 = tp_calc.calculate_short_tps(100.0, 105.0)
        assert tp1 > tp2 > tp3


class TestRiskManager:
    def test_risk_amount_calculation(self):
        rm = RiskManager()
        result = rm.calculate(entry_price=100.0, stop_loss=95.0, risk_percent=2.0, account_balance=10000.0)
        assert result.risk_amount == pytest.approx(200.0)

    def test_position_size_calculation(self):
        rm = RiskManager()
        result = rm.calculate(entry_price=100.0, stop_loss=95.0, risk_percent=2.0, account_balance=10000.0)
        # risk_amount=200, sl_distance=5 → position_size=40
        assert result.position_size == pytest.approx(40.0)

    def test_rr_ratio_calculated(self):
        rm = RiskManager()
        result = rm.calculate(entry_price=100.0, stop_loss=95.0, risk_percent=2.0, account_balance=10000.0, tp1=110.0)
        assert result.rr_ratio == pytest.approx(2.0)

    def test_max_loss_equals_risk_amount(self):
        rm = RiskManager()
        result = rm.calculate(entry_price=100.0, stop_loss=95.0, risk_percent=1.0, account_balance=5000.0)
        assert result.max_loss == pytest.approx(50.0)
