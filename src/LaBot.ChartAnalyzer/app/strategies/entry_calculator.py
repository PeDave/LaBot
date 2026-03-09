from __future__ import annotations

import logging

from app.api.models import EntryPoint, IndicatorSummary, PriceLevel

logger = logging.getLogger(__name__)


class EntryCalculator:
    """Calculates entry points: breakout, pullback, reversal."""

    def calculate_bullish_entry(
        self,
        indicators: IndicatorSummary,
        resistance_levels: list[PriceLevel],
        support_levels: list[PriceLevel],
    ) -> EntryPoint | None:
        current = indicators.current_price
        if current is None:
            return None

        # Breakout entry: above nearest resistance
        if resistance_levels:
            nearest_resistance = resistance_levels[0].price
            breakout_price = round(nearest_resistance * 1.005, 8)
            return EntryPoint(
                type="breakout",
                price=breakout_price,
                description=f"Breakout above resistance {nearest_resistance:.4f}",
            )

        # Pullback entry: if current price pulled back to EMA21 or support
        if indicators.ema_21 and current <= indicators.ema_21 * 1.01:
            return EntryPoint(
                type="pullback",
                price=round(indicators.ema_21, 8),
                description="Pullback to EMA21 support",
            )

        # Reversal entry: oversold RSI
        if indicators.rsi_signal == "oversold":
            return EntryPoint(
                type="reversal",
                price=round(current, 8),
                description="Reversal: RSI oversold bounce",
            )

        return EntryPoint(type="market", price=round(current, 8), description="Market entry")

    def calculate_bearish_entry(
        self,
        indicators: IndicatorSummary,
        resistance_levels: list[PriceLevel],
        support_levels: list[PriceLevel],
    ) -> EntryPoint | None:
        current = indicators.current_price
        if current is None:
            return None

        if support_levels:
            nearest_support = support_levels[0].price
            breakdown_price = round(nearest_support * 0.995, 8)
            return EntryPoint(
                type="breakdown",
                price=breakdown_price,
                description=f"Breakdown below support {nearest_support:.4f}",
            )

        if indicators.rsi_signal == "overbought":
            return EntryPoint(
                type="reversal",
                price=round(current, 8),
                description="Reversal: RSI overbought",
            )

        return EntryPoint(type="market", price=round(current, 8), description="Market entry (short)")
