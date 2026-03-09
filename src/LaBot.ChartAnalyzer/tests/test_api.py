"""FastAPI endpoint tests."""
from __future__ import annotations

import io
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.models import AnalysisReport, IndicatorSummary, Scenario
from app.main import app


def _mock_report(symbol: str = "BTC/USDT", timeframe: str = "4h") -> AnalysisReport:
    return AnalysisReport(
        symbol=symbol,
        timeframe=timeframe,
        timestamp=datetime.now(tz=timezone.utc),
        confidence=75.0,
        indicators=IndicatorSummary(current_price=50000.0, rsi=55.0, rsi_signal="neutral"),
        scenarios=[
            Scenario(direction="bullish", emoji="🟢", probability=55.0, actions=["Buy"]),
            Scenario(direction="bearish", emoji="🔴", probability=30.0, actions=["Sell"]),
            Scenario(direction="sideways", emoji="🟡", probability=15.0, actions=["Wait"]),
        ],
        summary="Test summary",
    )


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("app.api.routes.ollama_client.Client") as mock_ollama:
            mock_ollama.return_value.list.return_value = {}
            resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "ollama_connected" in data


@pytest.mark.asyncio
async def test_analyze_symbol_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("app.api.routes.analyzer.analyze_symbol", new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = _mock_report()
            resp = await client.post(
                "/api/v1/analyze/symbol",
                json={"symbol": "BTC/USDT", "timeframe": "4h", "risk_percent": 2.0, "account_balance": 10000.0},
            )
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "BTC/USDT"
    assert data["confidence"] == 75.0


@pytest.mark.asyncio
async def test_analyze_image_endpoint():
    fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("app.api.routes.analyzer.analyze_image", new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = _mock_report()
            resp = await client.post(
                "/api/v1/analyze/image",
                files={"file": ("test.png", fake_image, "image/png")},
                params={"timeframe": "4h", "risk_percent": 2.0},
            )
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "BTC/USDT"


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "LaBot Chart Analyzer"
