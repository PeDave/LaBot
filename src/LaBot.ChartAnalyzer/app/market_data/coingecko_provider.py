from __future__ import annotations

import logging

import httpx
import pandas as pd

from app.config import settings
from app.market_data.providers import MarketDataProvider

logger = logging.getLogger(__name__)

SYMBOL_MAP = {
    "BTC/USDT": "bitcoin",
    "ETH/USDT": "ethereum",
    "BNB/USDT": "binancecoin",
    "SOL/USDT": "solana",
    "XRP/USDT": "ripple",
    "ADA/USDT": "cardano",
    "DOGE/USDT": "dogecoin",
    "DOT/USDT": "polkadot",
    "AVAX/USDT": "avalanche-2",
    "MATIC/USDT": "matic-network",
}

TIMEFRAME_DAYS_MAP = {
    "15m": 1,
    "30m": 1,
    "1h": 7,
    "4h": 30,
    "1d": 365,
}


class CoinGeckoProvider(MarketDataProvider):
    """Fallback OHLCV provider using CoinGecko API."""

    BASE_URL = "https://api.coingecko.com/api/v3"

    async def fetch_ohlcv(
        self, symbol: str, timeframe: str = "4h", limit: int = 300
    ) -> pd.DataFrame:
        coin_id = SYMBOL_MAP.get(symbol.upper(), symbol.split("/")[0].lower())
        days = TIMEFRAME_DAYS_MAP.get(timeframe, 30)
        headers = {}
        if settings.coingecko_api_key:
            headers["x-cg-pro-api-key"] = settings.coingecko_api_key

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.BASE_URL}/coins/{coin_id}/ohlc",
                params={"vs_currency": "usd", "days": str(days)},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["volume"] = 0.0
        df = df.set_index("timestamp")
        return df
