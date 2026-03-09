from __future__ import annotations

import logging

from app.api.models import (
    DetectedPattern,
    EntryPoint,
    IndicatorSummary,
    PriceLevel,
    Scenario,
)
from app.strategies.entry_calculator import EntryCalculator
from app.strategies.stop_loss import StopLossCalculator
from app.strategies.take_profit import TakeProfitCalculator

logger = logging.getLogger(__name__)


class ScenarioBuilder:
    """Builds Bullish, Bearish, Sideways scenarios with probabilities."""

    # Scoring weights
    WEIGHTS = {
        "macd_bullish_crossover": 15,
        "macd_bearish_crossover": -15,
        "rsi_oversold": 10,
        "rsi_overbought": -10,
        "golden_cross": 20,
        "death_cross": -20,
        "bb_squeeze_breakout_up": 8,
        "volume_above_average": 5,
        "bullish_pattern": 10,
        "bearish_pattern": -10,
        "price_above_ema50": 8,
        "price_below_ema50": -8,
        "stoch_oversold": 7,
        "stoch_overbought": -7,
    }

    def __init__(self) -> None:
        self._entry_calc = EntryCalculator()
        self._sl_calc = StopLossCalculator()
        self._tp_calc = TakeProfitCalculator()

    def build(
        self,
        indicators: IndicatorSummary,
        patterns: list[DetectedPattern],
        support_levels: list[PriceLevel],
        resistance_levels: list[PriceLevel],
    ) -> list[Scenario]:
        score = self._calculate_score(indicators, patterns)
        bull_prob, bear_prob, side_prob = self._score_to_probabilities(score)

        bullish = self._build_bullish(indicators, patterns, support_levels, resistance_levels, bull_prob)
        bearish = self._build_bearish(indicators, patterns, support_levels, resistance_levels, bear_prob)
        sideways = self._build_sideways(indicators, side_prob)

        return [bullish, bearish, sideways]

    def _calculate_score(self, indicators: IndicatorSummary, patterns: list[DetectedPattern]) -> float:
        score = 0.0
        if indicators.macd_crossover == "bullish":
            score += self.WEIGHTS["macd_bullish_crossover"]
        elif indicators.macd_crossover == "bearish":
            score += self.WEIGHTS["macd_bearish_crossover"]
        if indicators.rsi_signal == "oversold":
            score += self.WEIGHTS["rsi_oversold"]
        elif indicators.rsi_signal == "overbought":
            score += self.WEIGHTS["rsi_overbought"]
        if indicators.golden_cross:
            score += self.WEIGHTS["golden_cross"]
        if indicators.death_cross:
            score += self.WEIGHTS["death_cross"]
        if indicators.volume_above_average:
            score += self.WEIGHTS["volume_above_average"]
        if indicators.current_price and indicators.ema_50:
            if indicators.current_price > indicators.ema_50:
                score += self.WEIGHTS["price_above_ema50"]
            else:
                score += self.WEIGHTS["price_below_ema50"]
        if indicators.stoch_k is not None:
            if indicators.stoch_k < 20:
                score += self.WEIGHTS["stoch_oversold"]
            elif indicators.stoch_k > 80:
                score += self.WEIGHTS["stoch_overbought"]
        for pattern in patterns:
            if pattern.direction == "bullish":
                score += self.WEIGHTS["bullish_pattern"] * pattern.confidence
            elif pattern.direction == "bearish":
                score += self.WEIGHTS["bearish_pattern"] * pattern.confidence
        return score

    def _score_to_probabilities(self, score: float) -> tuple[float, float, float]:
        """Convert raw score to bullish/bearish/sideways probabilities (sum = 100)."""
        max_score = 80.0
        normalized = max(min(score / max_score, 1.0), -1.0)
        if normalized >= 0:
            bull_prob = 40 + normalized * 35
            bear_prob = 15 + (1 - normalized) * 20
        else:
            bear_prob = 40 + abs(normalized) * 35
            bull_prob = 15 + (1 - abs(normalized)) * 20
        side_prob = 100.0 - bull_prob - bear_prob
        side_prob = max(side_prob, 5.0)
        total = bull_prob + bear_prob + side_prob
        return round(bull_prob / total * 100, 1), round(bear_prob / total * 100, 1), round(side_prob / total * 100, 1)

    def _build_bullish(
        self,
        indicators: IndicatorSummary,
        patterns: list[DetectedPattern],
        support_levels: list[PriceLevel],
        resistance_levels: list[PriceLevel],
        probability: float,
    ) -> Scenario:
        entry = self._entry_calc.calculate_bullish_entry(indicators, resistance_levels, support_levels)
        stop_loss = None
        tp1 = tp2 = tp3 = None
        rr = None
        if entry and indicators.current_price:
            stop_loss = self._sl_calc.calculate_long_sl(entry.price, indicators, support_levels)
            tp1, tp2, tp3 = self._tp_calc.calculate_long_tps(entry.price, stop_loss)
            risk = entry.price - stop_loss
            if risk > 0:
                rr = round((tp1 - entry.price) / risk, 2)

        actions = self._bullish_actions(indicators, patterns)

        return Scenario(
            direction="bullish",
            emoji="🟢",
            probability=probability,
            entry=entry,
            stop_loss=stop_loss,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            rr_ratio=rr,
            actions=actions,
        )

    def _build_bearish(
        self,
        indicators: IndicatorSummary,
        patterns: list[DetectedPattern],
        support_levels: list[PriceLevel],
        resistance_levels: list[PriceLevel],
        probability: float,
    ) -> Scenario:
        entry = self._entry_calc.calculate_bearish_entry(indicators, resistance_levels, support_levels)
        stop_loss = None
        tp1 = tp2 = tp3 = None
        rr = None
        if entry and indicators.current_price:
            stop_loss = self._sl_calc.calculate_short_sl(entry.price, indicators, resistance_levels)
            tp1, tp2, tp3 = self._tp_calc.calculate_short_tps(entry.price, stop_loss)
            risk = stop_loss - entry.price
            if risk > 0:
                rr = round((entry.price - tp1) / risk, 2)

        actions = self._bearish_actions(indicators, patterns)

        return Scenario(
            direction="bearish",
            emoji="🔴",
            probability=probability,
            entry=entry,
            stop_loss=stop_loss,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            rr_ratio=rr,
            actions=actions,
        )

    def _build_sideways(self, indicators: IndicatorSummary, probability: float) -> Scenario:
        actions = [
            "Várd meg a kitörést a range-ből",
            "Figyelj a volume növekedésre",
            "Állíts be árriasztást a key szintekre",
        ]
        if indicators.bb_squeeze:
            actions.insert(0, "Bollinger squeeze – erős mozgás várható")

        return Scenario(
            direction="sideways",
            emoji="🟡",
            probability=probability,
            actions=actions,
        )

    def _bullish_actions(self, indicators: IndicatorSummary, patterns: list[DetectedPattern]) -> list[str]:
        actions = []
        if indicators.macd_crossover == "bullish":
            actions.append("MACD bullish crossover – vételi jel")
        if indicators.rsi_signal == "oversold":
            actions.append("RSI túladott zónából pattan – jó vételi lehetőség")
        if indicators.golden_cross:
            actions.append("Golden Cross (SMA50 > SMA200) – erős bullish trend")
        if indicators.volume_above_average:
            actions.append("Átlag feletti volume megerősíti a mozgást")
        for p in patterns:
            if p.direction == "bullish":
                actions.append(f"Bullish minta: {p.name} ({p.confidence*100:.0f}%)")
        if not actions:
            actions.append("Nincs erős bullish jel, óvatosan!")
        return actions

    def _bearish_actions(self, indicators: IndicatorSummary, patterns: list[DetectedPattern]) -> list[str]:
        actions = []
        if indicators.macd_crossover == "bearish":
            actions.append("MACD bearish crossover – eladási jel")
        if indicators.rsi_signal == "overbought":
            actions.append("RSI túlvett zónában – eladási nyomás várható")
        if indicators.death_cross:
            actions.append("Death Cross (SMA50 < SMA200) – erős bearish trend")
        for p in patterns:
            if p.direction == "bearish":
                actions.append(f"Bearish minta: {p.name} ({p.confidence*100:.0f}%)")
        if not actions:
            actions.append("Nincs erős bearish jel, várj megerősítésre")
        return actions
