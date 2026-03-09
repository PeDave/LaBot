from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from app.api.models import DetectedPattern

logger = logging.getLogger(__name__)

MIN_CANDLES = 20


def _find_pivots(series: pd.Series, window: int = 5) -> tuple[list[int], list[int]]:
    """Find local highs and lows (pivot points)."""
    highs, lows = [], []
    for i in range(window, len(series) - window):
        if series.iloc[i] == series.iloc[i - window : i + window + 1].max():
            highs.append(i)
        if series.iloc[i] == series.iloc[i - window : i + window + 1].min():
            lows.append(i)
    return highs, lows


class PatternDetector:
    """Algorithmic chart pattern detection using pivot points."""

    def detect(self, df: pd.DataFrame) -> list[DetectedPattern]:
        if len(df) < MIN_CANDLES:
            return []

        close = df["close"]
        high = df["high"]
        low = df["low"]
        patterns: list[DetectedPattern] = []

        pivot_highs, pivot_lows = _find_pivots(close)

        patterns.extend(self._detect_head_and_shoulders(close, pivot_highs, pivot_lows))
        patterns.extend(self._detect_double_top_bottom(close, pivot_highs, pivot_lows))
        patterns.extend(self._detect_triangles(close, pivot_highs, pivot_lows))
        patterns.extend(self._detect_flags(close, high, low))
        patterns.extend(self._detect_wedges(close, pivot_highs, pivot_lows))

        return patterns

    def _detect_head_and_shoulders(
        self, close: pd.Series, highs: list[int], lows: list[int]
    ) -> list[DetectedPattern]:
        patterns = []
        if len(highs) < 3:
            return patterns
        for i in range(len(highs) - 2):
            l, m, r = highs[i], highs[i + 1], highs[i + 2]
            lv, mv, rv = float(close.iloc[l]), float(close.iloc[m]), float(close.iloc[r])
            if mv > lv and mv > rv and abs(lv - rv) / mv < 0.05:
                patterns.append(DetectedPattern(
                    name="Head & Shoulders",
                    confidence=0.65,
                    direction="bearish",
                    description="Bearish reversal pattern detected",
                ))
            if mv < lv and mv < rv and abs(lv - rv) / max(lv, rv) < 0.05:
                patterns.append(DetectedPattern(
                    name="Inverse Head & Shoulders",
                    confidence=0.65,
                    direction="bullish",
                    description="Bullish reversal pattern detected",
                ))
        return patterns

    def _detect_double_top_bottom(
        self, close: pd.Series, highs: list[int], lows: list[int]
    ) -> list[DetectedPattern]:
        patterns = []
        if len(highs) >= 2:
            l, r = highs[-2], highs[-1]
            lv, rv = float(close.iloc[l]), float(close.iloc[r])
            if abs(lv - rv) / max(lv, rv) < 0.03:
                patterns.append(DetectedPattern(
                    name="Double Top",
                    confidence=0.70,
                    direction="bearish",
                    description="Double top resistance pattern",
                ))
        if len(lows) >= 2:
            l, r = lows[-2], lows[-1]
            lv, rv = float(close.iloc[l]), float(close.iloc[r])
            if abs(lv - rv) / max(lv, rv) < 0.03:
                patterns.append(DetectedPattern(
                    name="Double Bottom",
                    confidence=0.70,
                    direction="bullish",
                    description="Double bottom support pattern",
                ))
        return patterns

    def _detect_triangles(
        self, close: pd.Series, highs: list[int], lows: list[int]
    ) -> list[DetectedPattern]:
        patterns = []
        if len(highs) < 2 or len(lows) < 2:
            return patterns
        h1, h2 = float(close.iloc[highs[-2]]), float(close.iloc[highs[-1]])
        l1, l2 = float(close.iloc[lows[-2]]), float(close.iloc[lows[-1]])
        highs_slope = h2 - h1
        lows_slope = l2 - l1
        if highs_slope < 0 and lows_slope > 0:
            patterns.append(DetectedPattern(
                name="Symmetrical Triangle",
                confidence=0.60,
                direction="neutral",
                description="Consolidation pattern, breakout expected",
            ))
        elif highs_slope < -0.005 and abs(lows_slope) < 0.002:
            patterns.append(DetectedPattern(
                name="Descending Triangle",
                confidence=0.65,
                direction="bearish",
                description="Bearish continuation pattern",
            ))
        elif lows_slope > 0.005 and abs(highs_slope) < 0.002:
            patterns.append(DetectedPattern(
                name="Ascending Triangle",
                confidence=0.65,
                direction="bullish",
                description="Bullish continuation pattern",
            ))
        return patterns

    def _detect_flags(
        self, close: pd.Series, high: pd.Series, low: pd.Series
    ) -> list[DetectedPattern]:
        patterns = []
        if len(close) < 20:
            return patterns
        pole_window = 10
        flag_window = 10
        pole = close.iloc[-flag_window - pole_window : -flag_window]
        flag = close.iloc[-flag_window:]
        pole_change = (float(pole.iloc[-1]) - float(pole.iloc[0])) / float(pole.iloc[0])
        flag_range = float(flag.max()) - float(flag.min())
        flag_avg = float(flag.mean())
        if pole_change > 0.05 and flag_range / flag_avg < 0.04:
            patterns.append(DetectedPattern(
                name="Bull Flag",
                confidence=0.60,
                direction="bullish",
                description="Bullish continuation after strong up-move",
            ))
        elif pole_change < -0.05 and flag_range / flag_avg < 0.04:
            patterns.append(DetectedPattern(
                name="Bear Flag",
                confidence=0.60,
                direction="bearish",
                description="Bearish continuation after strong down-move",
            ))
        return patterns

    def _detect_wedges(
        self, close: pd.Series, highs: list[int], lows: list[int]
    ) -> list[DetectedPattern]:
        patterns = []
        if len(highs) < 2 or len(lows) < 2:
            return patterns
        h1, h2 = float(close.iloc[highs[-2]]), float(close.iloc[highs[-1]])
        l1, l2 = float(close.iloc[lows[-2]]), float(close.iloc[lows[-1]])
        if h2 > h1 and l2 > l1 and (h2 - h1) < (l2 - l1):
            patterns.append(DetectedPattern(
                name="Rising Wedge",
                confidence=0.58,
                direction="bearish",
                description="Bearish reversal wedge pattern",
            ))
        elif h2 < h1 and l2 < l1 and abs(h2 - h1) < abs(l2 - l1):
            patterns.append(DetectedPattern(
                name="Falling Wedge",
                confidence=0.58,
                direction="bullish",
                description="Bullish reversal wedge pattern",
            ))
        return patterns
