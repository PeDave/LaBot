from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from app.api.models import PriceLevel

logger = logging.getLogger(__name__)

CLUSTER_TOLERANCE = 0.015  # 1.5% price clustering tolerance


class SupportResistanceDetector:
    """Detects support and resistance levels using pivot points and volume weighting."""

    def detect(
        self, df: pd.DataFrame, window: int = 5, max_levels: int = 5
    ) -> tuple[list[PriceLevel], list[PriceLevel]]:
        if len(df) < window * 2 + 1:
            return [], []

        close = df["close"]
        high = df["high"]
        low = df["low"]
        current_price = float(close.iloc[-1])

        pivot_highs = self._find_pivot_highs(high, window)
        pivot_lows = self._find_pivot_lows(low, window)

        support_prices = self._cluster_levels(pivot_lows)
        resistance_prices = self._cluster_levels(pivot_highs)

        support_levels = [
            PriceLevel(price=p, strength=self._calc_strength(p, pivot_lows), touches=self._count_touches(p, pivot_lows))
            for p in support_prices
            if p < current_price
        ]
        resistance_levels = [
            PriceLevel(price=p, strength=self._calc_strength(p, pivot_highs), touches=self._count_touches(p, pivot_highs))
            for p in resistance_prices
            if p > current_price
        ]

        support_levels.sort(key=lambda x: x.price, reverse=True)
        resistance_levels.sort(key=lambda x: x.price)

        return support_levels[:max_levels], resistance_levels[:max_levels]

    def _find_pivot_highs(self, high: pd.Series, window: int) -> list[float]:
        pivots = []
        for i in range(window, len(high) - window):
            if float(high.iloc[i]) == float(high.iloc[i - window : i + window + 1].max()):
                pivots.append(float(high.iloc[i]))
        return pivots

    def _find_pivot_lows(self, low: pd.Series, window: int) -> list[float]:
        pivots = []
        for i in range(window, len(low) - window):
            if float(low.iloc[i]) == float(low.iloc[i - window : i + window + 1].min()):
                pivots.append(float(low.iloc[i]))
        return pivots

    def _cluster_levels(self, prices: list[float]) -> list[float]:
        if not prices:
            return []
        sorted_prices = sorted(prices)
        clusters: list[list[float]] = []
        current_cluster = [sorted_prices[0]]
        for price in sorted_prices[1:]:
            if price <= current_cluster[0] * (1 + CLUSTER_TOLERANCE):
                current_cluster.append(price)
            else:
                clusters.append(current_cluster)
                current_cluster = [price]
        clusters.append(current_cluster)
        return [sum(c) / len(c) for c in clusters]

    def _calc_strength(self, price: float, pivots: list[float]) -> float:
        count = sum(1 for p in pivots if abs(p - price) / price < CLUSTER_TOLERANCE)
        return min(count / 5.0, 1.0)

    def _count_touches(self, price: float, pivots: list[float]) -> int:
        return sum(1 for p in pivots if abs(p - price) / price < CLUSTER_TOLERANCE)
