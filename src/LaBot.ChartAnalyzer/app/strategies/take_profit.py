from __future__ import annotations

import logging

from app.api.models import FibonacciLevels

logger = logging.getLogger(__name__)


class TakeProfitCalculator:
    """Calculates TP1, TP2, TP3 levels based on R:R ratios and Fibonacci extensions."""

    def calculate_long_tps(
        self,
        entry: float,
        stop_loss: float,
        fibonacci: FibonacciLevels | None = None,
    ) -> tuple[float, float, float]:
        risk = entry - stop_loss
        if risk <= 0:
            risk = entry * 0.02

        tp1 = round(entry + risk * 1.0, 8)   # 1:1 R:R
        tp2 = round(entry + risk * 2.0, 8)   # 1:2 R:R
        tp3 = round(entry + risk * 3.0, 8)   # 1:3 R:R

        # Override with Fibonacci extensions if available
        if fibonacci and fibonacci.extensions:
            ext_values = sorted(fibonacci.extensions.values())
            if len(ext_values) >= 1 and ext_values[0] > entry:
                tp1 = round(ext_values[0], 8)
            if len(ext_values) >= 2 and ext_values[1] > entry:
                tp2 = round(ext_values[1], 8)
            if len(ext_values) >= 3 and ext_values[2] > entry:
                tp3 = round(ext_values[2], 8)

        return tp1, tp2, tp3

    def calculate_short_tps(
        self,
        entry: float,
        stop_loss: float,
        fibonacci: FibonacciLevels | None = None,
    ) -> tuple[float, float, float]:
        risk = stop_loss - entry
        if risk <= 0:
            risk = entry * 0.02

        tp1 = round(entry - risk * 1.0, 8)
        tp2 = round(entry - risk * 2.0, 8)
        tp3 = round(entry - risk * 3.0, 8)

        return tp1, tp2, tp3
