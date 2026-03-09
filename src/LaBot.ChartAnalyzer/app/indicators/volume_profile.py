from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class VolumeProfileAnalyzer:
    """Analyzes volume distribution across price levels."""

    def analyze(self, df: pd.DataFrame, bins: int = 20) -> dict:
        if "volume" not in df.columns or len(df) < 10:
            return {}

        price_min = float(df["low"].min())
        price_max = float(df["high"].max())
        price_range = price_max - price_min

        if price_range == 0:
            return {}

        bin_size = price_range / bins
        volume_profile: dict[float, float] = {}

        for _, row in df.iterrows():
            typical_price = (row["high"] + row["low"] + row["close"]) / 3.0
            bin_idx = int((typical_price - price_min) / bin_size)
            bin_idx = min(bin_idx, bins - 1)
            bin_price = price_min + bin_idx * bin_size
            volume_profile[bin_price] = volume_profile.get(bin_price, 0) + float(row["volume"])

        if not volume_profile:
            return {}

        poc_price = max(volume_profile, key=lambda k: volume_profile[k])
        sorted_volumes = sorted(volume_profile.values(), reverse=True)
        total_volume = sum(sorted_volumes)
        value_area_volume = total_volume * 0.70
        cumulative = 0.0
        value_area_prices = []
        for price, vol in sorted(volume_profile.items(), key=lambda x: x[1], reverse=True):
            cumulative += vol
            value_area_prices.append(price)
            if cumulative >= value_area_volume:
                break

        vah = max(value_area_prices) if value_area_prices else price_max
        val = min(value_area_prices) if value_area_prices else price_min

        return {
            "poc": poc_price,
            "vah": vah,
            "val": val,
            "profile": volume_profile,
        }
