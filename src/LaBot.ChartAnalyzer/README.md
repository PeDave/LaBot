# LaBot Chart Analyzer

AI-alapú kriptovaluta technikai elemzési szolgáltatás – FastAPI + Ollama (LLaVA) + pandas-ta.

## Funkciók

- 📸 **Kép elemzés** – Chart képernyőkép feltöltése, LLaVA multimodális AI értelmezi
- 📈 **Szimbólum elemzés** – Élő OHLCV adat letöltése Binance-ről (CoinGecko fallback), teljes technikai elemzés
- 🔀 **Kombinált elemzés** – Kép AI + élő adatok együtt
- 📊 **Indikátorok**: RSI, MACD, Bollinger Bands, EMA 9/21/50/200, SMA 50/200, ATR, Stochastic RSI
- 🔍 **Chart minták**: Head & Shoulders, Double Top/Bottom, Triangle, Flag, Wedge
- 📐 **Fibonacci** retracement és extension szintek
- 🎯 **Support/Resistance** automatikus detektálás
- 🟢🔴🟡 **3 forgatókönyv** (Bullish/Bearish/Sideways) valószínűségekkel
- 💰 **Kockázatkezelés** – Pozícióméret, SL, TP1/TP2/TP3, R:R arány
- 🖥️ **Streamlit UI** vizuális dashboardhoz

---

## Gyors indítás

### Követelmények

- Python 3.12+
- [Ollama](https://ollama.ai) futó instance LLaVA modellel (kép elemzéshez)

### Telepítés

```bash
cd src/LaBot.ChartAnalyzer
pip install -r requirements.txt
```

### Futtatás

```bash
# API szerver
uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload

# Streamlit UI (külön terminálban)
streamlit run app/ui/streamlit_app.py
```

### Docker Compose

```bash
docker-compose up -d
```

---

## API Végpontok

| Metódus | Végpont | Leírás |
|---------|---------|--------|
| `GET` | `/` | Service info |
| `GET` | `/api/v1/health` | Health check (Ollama állapot) |
| `POST` | `/api/v1/analyze/image` | Chart kép elemzés (multipart) |
| `POST` | `/api/v1/analyze/symbol` | Szimbólum elemzés (JSON) |
| `POST` | `/api/v1/analyze/combined` | Kombinált kép + szimbólum (multipart) |

Interaktív API docs: [http://localhost:8100/docs](http://localhost:8100/docs)

### Példa: Szimbólum elemzés

```bash
curl -X POST http://localhost:8100/api/v1/analyze/symbol \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC/USDT", "timeframe": "4h", "risk_percent": 2.0, "account_balance": 10000}'
```

### Példa: Kép elemzés

```bash
curl -X POST http://localhost:8100/api/v1/analyze/image \
  -F "file=@chart.png" \
  -F "timeframe=4h" \
  -F "risk_percent=2.0"
```

---

## Konfiguráció

Másold `.env.example` → `.env` és töltsd ki:

| Változó | Alapértelmezett | Leírás |
|---------|----------------|--------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama szerver URL |
| `OLLAMA_MODEL` | `llava:13b` | LLaVA modell neve |
| `API_HOST` | `0.0.0.0` | API szerver host |
| `API_PORT` | `8100` | API szerver port |
| `BINANCE_API_KEY` | _(üres)_ | Opcionális, magasabb rate limithez |
| `COINGECKO_API_KEY` | _(üres)_ | Opcionális CoinGecko Pro |
| `DEFAULT_RISK_PERCENT` | `2.0` | Alapértelmezett kockázat % |
| `DEFAULT_ACCOUNT_BALANCE` | `10000` | Alapértelmezett számlaegyenleg |
| `REPORT_LANGUAGE` | `hu` | Riport nyelve |

---

## Tesztek futtatása

```bash
cd src/LaBot.ChartAnalyzer
python -m pytest tests/ -v
```

---

## Projekt struktúra

```
app/
├── main.py              # FastAPI alkalmazás
├── config.py            # Konfiguráció (pydantic-settings)
├── api/
│   ├── routes.py        # API végpontok
│   └── models.py        # Pydantic modellek
├── core/
│   ├── analyzer.py      # Fő orchestrátor
│   ├── image_analyzer.py # Ollama/LLaVA integráció
│   ├── data_analyzer.py  # OHLCV elemzés orchestrátor
│   └── report_generator.py # Riport összeállítás
├── indicators/
│   ├── technical.py     # RSI, MACD, BB, EMA, ATR, stb.
│   ├── patterns.py      # Chart minta detektálás
│   ├── fibonacci.py     # Fibonacci szintek
│   ├── support_resistance.py # S/R szint detektálás
│   └── volume_profile.py # Volume profil analízis
├── market_data/
│   ├── providers.py     # Abstract provider + factory
│   ├── binance_provider.py # Binance ccxt integráció
│   └── coingecko_provider.py # CoinGecko fallback
├── strategies/
│   ├── entry_calculator.py # Entry pont számítás
│   ├── stop_loss.py     # Stop loss számítás
│   ├── take_profit.py   # TP1/TP2/TP3 számítás
│   └── risk_manager.py  # Pozícióméret és kockázat
├── scenarios/
│   └── scenario_builder.py # Bullish/Bearish/Sideways
└── ui/
    └── streamlit_app.py # Streamlit dashboard
```

---

## Integráció LaBot.Api-val

A Chart Analyzer önálló HTTP szolgáltatásként fut. A LaBot.Api .NET projekt `HttpClient`-tel hívhatja:

```csharp
var response = await httpClient.PostAsJsonAsync(
    "http://chart-analyzer:8100/api/v1/analyze/symbol",
    new { symbol = "BTC/USDT", timeframe = "4h", risk_percent = 2.0, account_balance = 10000 }
);
var report = await response.Content.ReadFromJsonAsync<AnalysisReport>();
```

---

## Licenc

MIT – LaBot projekt része.
