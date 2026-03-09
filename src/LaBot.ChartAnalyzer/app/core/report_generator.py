from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.api.models import AnalysisReport, IndicatorSummary, RiskAssessment, Scenario
from app.scenarios.scenario_builder import ScenarioBuilder
from app.strategies.risk_manager import RiskManager

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Assembles the final AnalysisReport from all analysis components."""

    def __init__(self) -> None:
        self._scenario_builder = ScenarioBuilder()
        self._risk_manager = RiskManager()

    def generate(
        self,
        symbol: str,
        timeframe: str,
        analysis: dict,
        risk_percent: float = 2.0,
        account_balance: float = 10000.0,
        ai_interpretation: str | None = None,
    ) -> AnalysisReport:
        indicators: IndicatorSummary = analysis.get("indicators", IndicatorSummary())
        patterns = analysis.get("patterns", [])
        support_levels = analysis.get("support_levels", [])
        resistance_levels = analysis.get("resistance_levels", [])
        fibonacci = analysis.get("fibonacci")

        scenarios: list[Scenario] = self._scenario_builder.build(
            indicators=indicators,
            patterns=patterns,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
        )

        risk_assessment: RiskAssessment | None = None
        bullish_scenario = next((s for s in scenarios if s.direction == "bullish"), None)
        if bullish_scenario and bullish_scenario.entry and bullish_scenario.stop_loss:
            risk_assessment = self._risk_manager.calculate(
                entry_price=bullish_scenario.entry.price,
                stop_loss=bullish_scenario.stop_loss,
                risk_percent=risk_percent,
                account_balance=account_balance,
                tp1=bullish_scenario.tp1,
            )

        confidence = self._calculate_confidence(indicators, patterns, scenarios)
        summary = self._build_summary(symbol, timeframe, indicators, scenarios, confidence)

        return AnalysisReport(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.now(tz=timezone.utc),
            confidence=confidence,
            indicators=indicators,
            patterns=patterns,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            fibonacci=fibonacci,
            scenarios=scenarios,
            risk_assessment=risk_assessment,
            ai_interpretation=ai_interpretation,
            summary=summary,
        )

    def _calculate_confidence(
        self,
        indicators: IndicatorSummary,
        patterns: list,
        scenarios: list[Scenario],
    ) -> float:
        score = 50.0
        if indicators.macd_crossover != "none":
            score += 10
        if indicators.rsi_signal in ("oversold", "overbought"):
            score += 8
        if indicators.golden_cross:
            score += 12
        if indicators.death_cross:
            score += 12
        if patterns:
            score += min(len(patterns) * 5, 20)
        return min(score, 95.0)

    def _build_summary(
        self,
        symbol: str,
        timeframe: str,
        indicators: IndicatorSummary,
        scenarios: list[Scenario],
        confidence: float,
    ) -> str:
        bullish = next((s for s in scenarios if s.direction == "bullish"), None)
        bearish = next((s for s in scenarios if s.direction == "bearish"), None)
        dominant = max(scenarios, key=lambda s: s.probability) if scenarios else None
        direction_hu = {"bullish": "emelkedő", "bearish": "csökkenő", "sideways": "oldalazó"}.get(
            dominant.direction if dominant else "sideways", "oldalazó"
        )
        rsi_text = f"RSI: {indicators.rsi:.1f}" if indicators.rsi else ""
        return (
            f"{symbol} ({timeframe}) – {direction_hu} kilátás "
            f"({dominant.probability:.0f}% valószínűség). "
            f"Megbízhatóság: {confidence:.0f}%. "
            f"{rsi_text}. "
            f"Bullish valószínűség: {bullish.probability:.0f}% | Bearish: {bearish.probability:.0f}%."
            if bullish and bearish
            else f"{symbol} ({timeframe}) – Elemzés kész. Megbízhatóság: {confidence:.0f}%."
        )
