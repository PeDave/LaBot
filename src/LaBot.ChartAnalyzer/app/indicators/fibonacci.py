from __future__ import annotations

import pandas as pd

from app.api.models import FibonacciLevels

RETRACEMENT_LEVELS = {
    "0.236": 0.236,
    "0.382": 0.382,
    "0.500": 0.500,
    "0.618": 0.618,
    "0.786": 0.786,
}

EXTENSION_LEVELS = {
    "1.272": 1.272,
    "1.618": 1.618,
    "2.618": 2.618,
}


class FibonacciCalculator:
    """Calculates Fibonacci retracement and extension levels."""

    def calculate(self, df: pd.DataFrame, lookback: int = 50) -> FibonacciLevels:
        data = df.tail(lookback)
        swing_high = float(data["high"].max())
        swing_low = float(data["low"].min())
        diff = swing_high - swing_low

        retracements = {
            level: round(swing_high - diff * ratio, 8)
            for level, ratio in RETRACEMENT_LEVELS.items()
        }
        extensions = {
            level: round(swing_low + diff * ratio, 8)
            for level, ratio in EXTENSION_LEVELS.items()
        }

        return FibonacciLevels(
            swing_high=swing_high,
            swing_low=swing_low,
            retracements=retracements,
            extensions=extensions,
        )
