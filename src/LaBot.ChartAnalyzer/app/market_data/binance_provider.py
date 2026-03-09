from __future__ import annotations

import logging

import ccxt.async_support as ccxt
import pandas as pd

from app.config import settings
from app.market_data.providers import MarketDataProvider

logger = logging.getLogger(__name__)


class BinanceProvider(MarketDataProvider):
    """Fetches OHLCV data from Binance via ccxt."""

    def __init__(self) -> None:
        exchange_config: dict = {"enableRateLimit": True}
        if settings.binance_api_key:
            exchange_config["apiKey"] = settings.binance_api_key
        self._exchange = ccxt.binance(exchange_config)

    async def fetch_ohlcv(
        self, symbol: str, timeframe: str = "4h", limit: int = 300
    ) -> pd.DataFrame:
        try:
            raw = await self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            await self._exchange.close()
            df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.set_index("timestamp")
            return df
        except Exception as exc:
            logger.warning("Binance fetch failed for %s: %s. Falling back to CoinGecko.", symbol, exc)
            await self._exchange.close()
            from app.market_data.coingecko_provider import CoinGeckoProvider
            fallback = CoinGeckoProvider()
            return await fallback.fetch_ohlcv(symbol, timeframe, limit)
