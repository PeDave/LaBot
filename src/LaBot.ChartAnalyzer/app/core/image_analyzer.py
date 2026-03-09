from __future__ import annotations

import base64
import logging

import ollama

from app.config import settings

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """Elemezd ezt a kriptovaluta chart képet részletesen, magyarul. Kérlek vizsgáld meg:

1. **Candlestick minták**: Milyen candlestick formációkat látsz? (pl. Doji, Hammer, Engulfing, Morning Star stb.)
2. **Trendvonalak**: Milyen az aktuális trend? (emelkedő, csökkenő, oldalazó)
3. **Support és Resistance szintek**: Mely árak közelében láthatók fontos szintek?
4. **Technikai indikátorok**: Ha láthatóak indikátorok (RSI, MACD, Bollinger Bands stb.), olvasd le az értékeket.
5. **Chart minták**: Látható-e chart minta? (pl. Head & Shoulders, Double Top/Bottom, Triangle, Flag stb.)
6. **Általános hangulat**: Bullish, Bearish, vagy Neutral?
7. **Kereskedési javaslat**: Mit javasolsz rövidtávon?

Légy konkrét és precíz. Adj percentage valószínűségeket ahol lehetséges."""


class ImageAnalyzer:
    """Analyzes chart images using Ollama + LLaVA model."""

    def __init__(self) -> None:
        self._client = ollama.Client(host=settings.ollama_host)
        self._model = settings.ollama_model

    def analyze(self, image_bytes: bytes) -> str:
        """Send image to LLaVA for analysis. Returns raw text interpretation."""
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        try:
            response = self._client.chat(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": ANALYSIS_PROMPT,
                        "images": [image_b64],
                    }
                ],
            )
            return response["message"]["content"]
        except Exception as exc:
            logger.warning("Ollama image analysis failed: %s", exc)
            return f"AI elemzés nem elérhető: {exc}"
