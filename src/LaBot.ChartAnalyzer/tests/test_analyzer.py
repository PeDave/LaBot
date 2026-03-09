"""Unit tests for ChartAnalyzer orchestrator."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from app.core.analyzer import ChartAnalyzer
from app.api.models import AnalysisReport


def _make_df(n: int = 100) -> pd.DataFrame:
    np.random.seed(0)
    closes = np.cumsum(np.random.randn(n) * 2) + 100
    closes = np.maximum(closes, 1.0)
    df = pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, n),
    })
    return df


@pytest.mark.asyncio
async def test_analyze_symbol_returns_report():
    analyzer = ChartAnalyzer()
    mock_df = _make_df()
    with patch("app.market_data.binance_provider.BinanceProvider.fetch_ohlcv", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_df
        report = await analyzer.analyze_symbol("BTC/USDT", "4h", 2.0, 10000.0)
    assert isinstance(report, AnalysisReport)
    assert report.symbol == "BTC/USDT"
    assert report.timeframe == "4h"
    assert 0 <= report.confidence <= 100
    assert len(report.scenarios) == 3


@pytest.mark.asyncio
async def test_analyze_image_returns_report_with_ai():
    analyzer = ChartAnalyzer()
    with patch.object(analyzer._image_analyzer, "analyze", return_value="Mock AI analysis"):
        report = await analyzer.analyze_image(b"fake_image_bytes", "4h", 2.0)
    assert isinstance(report, AnalysisReport)
    assert report.ai_interpretation == "Mock AI analysis"


@pytest.mark.asyncio
async def test_analyze_combined_returns_report():
    analyzer = ChartAnalyzer()
    mock_df = _make_df()
    with patch.object(analyzer._image_analyzer, "analyze", return_value="AI text"), \
         patch("app.market_data.binance_provider.BinanceProvider.fetch_ohlcv", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_df
        report = await analyzer.analyze_combined(b"image", "BTC/USDT", "4h")
    assert isinstance(report, AnalysisReport)
    assert report.ai_interpretation == "AI text"
    assert report.symbol == "BTC/USDT"
