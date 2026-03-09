from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SymbolAnalysisRequest(BaseModel):
    symbol: str = Field(..., examples=["BTC/USDT"])
    timeframe: str = Field("4h", examples=["15m", "30m", "1h", "4h", "1d"])
    risk_percent: float = Field(2.0, ge=0.1, le=10.0)
    account_balance: float = Field(10000.0, ge=100.0)


class IndicatorSummary(BaseModel):
    rsi: Optional[float] = None
    rsi_signal: str = "neutral"  # oversold / overbought / neutral
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    macd_crossover: str = "none"  # bullish / bearish / none
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_squeeze: bool = False
    ema_9: Optional[float] = None
    ema_21: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    golden_cross: bool = False
    death_cross: bool = False
    atr: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    volume_above_average: bool = False
    current_price: Optional[float] = None


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
    entry: Optional[EntryPoint] = None
    stop_loss: Optional[float] = None
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    tp3: Optional[float] = None
    rr_ratio: Optional[float] = None
    actions: list[str] = []


class RiskAssessment(BaseModel):
    risk_percent: float
    account_balance: float
    risk_amount: float
    position_size: Optional[float] = None
    max_loss: Optional[float] = None
    rr_ratio: Optional[float] = None


class AnalysisReport(BaseModel):
    symbol: str
    timeframe: str
    timestamp: datetime
    confidence: float = Field(..., ge=0.0, le=100.0)
    indicators: IndicatorSummary
    patterns: list[DetectedPattern] = []
    support_levels: list[PriceLevel] = []
    resistance_levels: list[PriceLevel] = []
    fibonacci: Optional[FibonacciLevels] = None
    scenarios: list[Scenario] = []
    risk_assessment: Optional[RiskAssessment] = None
    ai_interpretation: Optional[str] = None
    summary: str = ""


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    model: str
