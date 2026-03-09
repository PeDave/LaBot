from __future__ import annotations

import logging

from app.api.models import IndicatorSummary, PriceLevel

logger = logging.getLogger(__name__)


class StopLossCalculator:
    """Calculates stop loss levels: ATR-based, structure-based, percentage-based."""

    def calculate_long_sl(
        self,
        entry: float,
        indicators: IndicatorSummary,
        support_levels: list[PriceLevel],
        atr_multiplier: float = 1.5,
        percentage: float = 0.02,
    ) -> float:
        # ATR-based SL
        if indicators.atr:
            atr_sl = entry - indicators.atr * atr_multiplier
            if support_levels:
                structure_sl = support_levels[0].price * 0.998
                return round(max(atr_sl, structure_sl) if atr_sl > 0 else structure_sl, 8)
            return round(atr_sl, 8)

        # Structure-based SL
        if support_levels:
            return round(support_levels[0].price * 0.998, 8)

        # Percentage-based fallback
        return round(entry * (1 - percentage), 8)

    def calculate_short_sl(
        self,
        entry: float,
        indicators: IndicatorSummary,
        resistance_levels: list[PriceLevel],
        atr_multiplier: float = 1.5,
        percentage: float = 0.02,
    ) -> float:
        if indicators.atr:
            atr_sl = entry + indicators.atr * atr_multiplier
            if resistance_levels:
                structure_sl = resistance_levels[0].price * 1.002
                return round(min(atr_sl, structure_sl), 8)
            return round(atr_sl, 8)

        if resistance_levels:
            return round(resistance_levels[0].price * 1.002, 8)

        return round(entry * (1 + percentage), 8)
