from __future__ import annotations

from typing import Annotated

import ollama as ollama_client
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.models import AnalysisReport, HealthResponse, SymbolAnalysisRequest
from app.config import settings
from app.core.analyzer import ChartAnalyzer

router = APIRouter()
analyzer = ChartAnalyzer()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    ollama_connected = False
    try:
        client = ollama_client.Client(host=settings.ollama_host)
        client.list()
        ollama_connected = True
    except Exception:
        pass

    return HealthResponse(
        status="ok",
        ollama_connected=ollama_connected,
        model=settings.ollama_model,
    )


@router.post("/analyze/image", response_model=AnalysisReport)
async def analyze_image(
    file: Annotated[UploadFile, File(description="Chart screenshot image")],
    timeframe: str = "4h",
    risk_percent: float = 2.0,
) -> AnalysisReport:
    """Analyze a chart image using AI (LLaVA via Ollama)."""
    if file.content_type not in ("image/png", "image/jpeg", "image/webp", "image/gif"):
        raise HTTPException(status_code=400, detail="Unsupported image format. Use PNG, JPEG, or WebP.")

    image_bytes = await file.read()
    report = await analyzer.analyze_image(
        image_bytes=image_bytes,
        timeframe=timeframe,
        risk_percent=risk_percent,
    )
    return report


@router.post("/analyze/symbol", response_model=AnalysisReport)
async def analyze_symbol(request: SymbolAnalysisRequest) -> AnalysisReport:
    """Analyze a trading symbol using live OHLCV data from Binance/CoinGecko."""
    report = await analyzer.analyze_symbol(
        symbol=request.symbol,
        timeframe=request.timeframe,
        risk_percent=request.risk_percent,
        account_balance=request.account_balance,
    )
    return report


@router.post("/analyze/combined", response_model=AnalysisReport)
async def analyze_combined(
    file: Annotated[UploadFile, File(description="Chart screenshot image")],
    symbol: Annotated[str, Form()] = "BTC/USDT",
    timeframe: Annotated[str, Form()] = "4h",
    risk_percent: Annotated[float, Form()] = 2.0,
    account_balance: Annotated[float, Form()] = 10000.0,
) -> AnalysisReport:
    """Combined analysis: image AI + live OHLCV data."""
    image_bytes = await file.read()
    report = await analyzer.analyze_combined(
        image_bytes=image_bytes,
        symbol=symbol,
        timeframe=timeframe,
        risk_percent=risk_percent,
        account_balance=account_balance,
    )
    return report
