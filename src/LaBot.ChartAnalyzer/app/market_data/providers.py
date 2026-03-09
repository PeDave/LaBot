from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from app.config import settings


class MarketDataProvider(ABC):
    """Abstract base class for market data providers."""

    @abstractmethod
    async def fetch_ohlcv(
        self, symbol: str, timeframe: str = "4h", limit: int = 300
    ) -> pd.DataFrame:
        """Fetch OHLCV data as a DataFrame with columns: timestamp, open, high, low, close, volume."""
        ...


def get_provider() -> MarketDataProvider:
    """Factory: returns primary (Binance) or fallback (CoinGecko) provider."""
    from app.market_data.binance_provider import BinanceProvider
    return BinanceProvider()
