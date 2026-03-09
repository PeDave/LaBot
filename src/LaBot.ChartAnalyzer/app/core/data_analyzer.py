from __future__ import annotations

import logging

import pandas as pd

from app.api.models import (
    DetectedPattern,
    FibonacciLevels,
    IndicatorSummary,
    PriceLevel,
)
from app.indicators.fibonacci import FibonacciCalculator
from app.indicators.patterns import PatternDetector
from app.indicators.support_resistance import SupportResistanceDetector
from app.indicators.technical import TechnicalIndicators
from app.indicators.volume_profile import VolumeProfileAnalyzer

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """Orchestrates all technical analysis on OHLCV data."""

    def __init__(self) -> None:
        self._tech = TechnicalIndicators()
        self._patterns = PatternDetector()
        self._fib = FibonacciCalculator()
        self._sr = SupportResistanceDetector()
        self._vol = VolumeProfileAnalyzer()

    def analyze(self, df: pd.DataFrame) -> dict:
        """Run all analyses and return results dict."""
        indicators = self._tech.calculate(df)
        patterns = self._patterns.detect(df)
        fib = self._fib.calculate(df)
        support, resistance = self._sr.detect(df)

        return {
            "indicators": indicators,
            "patterns": patterns,
            "fibonacci": fib,
            "support_levels": support,
            "resistance_levels": resistance,
        }
