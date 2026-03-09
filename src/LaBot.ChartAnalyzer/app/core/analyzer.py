from __future__ import annotations

import logging

import pandas as pd

from app.api.models import AnalysisReport, IndicatorSummary
from app.config import settings
from app.core.data_analyzer import DataAnalyzer
from app.core.image_analyzer import ImageAnalyzer
from app.core.report_generator import ReportGenerator
from app.market_data.providers import get_provider

logger = logging.getLogger(__name__)


class ChartAnalyzer:
    """Main orchestrator for all chart analysis types."""

    def __init__(self) -> None:
        self._image_analyzer = ImageAnalyzer()
        self._data_analyzer = DataAnalyzer()
        self._report_generator = ReportGenerator()

    async def analyze_image(
        self,
        image_bytes: bytes,
        timeframe: str = "4h",
        risk_percent: float = 2.0,
    ) -> AnalysisReport:
        """Analyze a chart image using AI only (no OHLCV data)."""
        ai_text = self._image_analyzer.analyze(image_bytes)
        empty_analysis: dict = {
            "indicators": IndicatorSummary(),
            "patterns": [],
            "support_levels": [],
            "resistance_levels": [],
            "fibonacci": None,
        }
        return self._report_generator.generate(
            symbol="UNKNOWN",
            timeframe=timeframe,
            analysis=empty_analysis,
            risk_percent=risk_percent,
            ai_interpretation=ai_text,
        )

    async def analyze_symbol(
        self,
        symbol: str,
        timeframe: str = "4h",
        risk_percent: float = 2.0,
        account_balance: float = 10000.0,
    ) -> AnalysisReport:
        """Fetch OHLCV data and run full technical analysis."""
        provider = get_provider()
        df = await provider.fetch_ohlcv(symbol=symbol, timeframe=timeframe)
        analysis = self._data_analyzer.analyze(df)
        return self._report_generator.generate(
            symbol=symbol,
            timeframe=timeframe,
            analysis=analysis,
            risk_percent=risk_percent,
            account_balance=account_balance,
        )

    async def analyze_combined(
        self,
        image_bytes: bytes,
        symbol: str = "BTC/USDT",
        timeframe: str = "4h",
        risk_percent: float = 2.0,
        account_balance: float = 10000.0,
    ) -> AnalysisReport:
        """Combined: AI image analysis + live OHLCV technical analysis."""
        ai_text = self._image_analyzer.analyze(image_bytes)
        provider = get_provider()
        df = await provider.fetch_ohlcv(symbol=symbol, timeframe=timeframe)
        analysis = self._data_analyzer.analyze(df)
        return self._report_generator.generate(
            symbol=symbol,
            timeframe=timeframe,
            analysis=analysis,
            risk_percent=risk_percent,
            account_balance=account_balance,
            ai_interpretation=ai_text,
        )
