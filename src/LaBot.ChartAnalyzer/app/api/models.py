from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SymbolAnalysisRequest(BaseModel):
    symbol: str = Field(..., examples=["BTC/USDT"])
    timeframe: str = Field("4h", examples=["15m", "30m", "1h", "4h", "1d"])
    risk_percent: float = Field(2.0, ge=0.1, le=10.0)
    account_balance: float = Field(10000.0, ge=100.0)


class IndicatorSummary(BaseModel):
    rsi: float | None = None
    rsi_signal: str = "neutral"  # oversold / overbought / neutral
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    macd_crossover: str = "none"  # bullish / bearish / none
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    bb_squeeze: bool = False
    ema_9: float | None = None
    ema_21: float | None = None
    ema_50: float | None = None
    ema_200: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None
    golden_cross: bool = False
    death_cross: bool = False
    atr: float | None = None
    stoch_k: float | None = None
    stoch_d: float | None = None
    volume_above_average: bool = False
    current_price: float | None = None


class DetectedPattern(BaseModel):
    name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    direction: str  # bullish / bearish / neutral
    description: str = ""


class PriceLevel(BaseModel):
    price: float
    strength: float = Field(..., ge=0.0, le=1.0)
    touches: int = 1


class FibonacciLevels(BaseModel):
    swing_high: float
    swing_low: float
    retracements: dict[str, float] = {}
    extensions: dict[str, float] = {}


class EntryPoint(BaseModel):
    type: str  # breakout / pullback / reversal
    price: float
    description: str = ""


class Scenario(BaseModel):
    direction: str  # bullish / bearish / sideways
    emoji: str
    probability: float = Field(..., ge=0.0, le=100.0)
    entry: EntryPoint | None = None
    stop_loss: float | None = None
    tp1: float | None = None
    tp2: float | None = None
    tp3: float | None = None
    rr_ratio: float | None = None
    actions: list[str] = []


class RiskAssessment(BaseModel):
    risk_percent: float
    account_balance: float
    risk_amount: float
    position_size: float | None = None
    max_loss: float | None = None
    rr_ratio: float | None = None


class AnalysisReport(BaseModel):
    symbol: str
    timeframe: str
    timestamp: datetime
    confidence: float = Field(..., ge=0.0, le=100.0)
    indicators: IndicatorSummary
    patterns: list[DetectedPattern] = []
    support_levels: list[PriceLevel] = []
    resistance_levels: list[PriceLevel] = []
    fibonacci: FibonacciLevels | None = None
    scenarios: list[Scenario] = []
    risk_assessment: RiskAssessment | None = None
    ai_interpretation: str | None = None
    summary: str = ""


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    model: str
