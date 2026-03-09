# LaBot Chart Analyzer – Technikai Dokumentáció

## Áttekintés

A **LaBot Chart Analyzer** egy önálló Python-alapú mikroszolgáltatás, amely AI-alapú és algoritmikus technikai elemzést végez kriptovaluta chartokra. FastAPI keretrendszert használ REST API-ként, és képes:

- Multimodális AI képelemzésre (Ollama + LLaVA)
- Valós idejű OHLCV adatlekérésre (Binance / CoinGecko)
- Teljes technikai indikátor számításra (pandas-ta)
- Chart minta felismerésre (algoritmikus pivot analízis)
- Kereskedési forgatókönyvek generálására valószínűségekkel
- Kockázatkezelési számításokra (pozícióméret, SL, TP)

---

## Architektúra

```
┌─────────────────────────────────────────────────────┐
│                   FastAPI (port 8100)                │
│  POST /analyze/image                                 │
│  POST /analyze/symbol                                │
│  POST /analyze/combined                              │
└────────────────────┬────────────────────────────────┘
                     │
              ChartAnalyzer (orchestrátor)
             /         |          \
   ImageAnalyzer   DataAnalyzer   ReportGenerator
        │               │               │
   Ollama/LLaVA   TechnicalIndicators  ScenarioBuilder
                  PatternDetector      RiskManager
                  FibonacciCalculator
                  SupportResistance
                  VolumeProfile
                       │
              MarketDataProvider
              /              \
    BinanceProvider     CoinGeckoProvider
```

---

## Modulok részletes leírása

### `app/config.py`
`pydantic-settings` alapú konfiguráció. Beolvassa a `.env` fájlt vagy környezeti változókat. Singleton `settings` objektum exportálva.

### `app/api/models.py`
Összes Pydantic v2 adatmodell:
- `SymbolAnalysisRequest` – API kérés body
- `IndicatorSummary` – Összes indikátor értéke
- `DetectedPattern` – Felismert chart minta
- `PriceLevel` – Support/Resistance szint
- `FibonacciLevels` – Fib retracement/extension szintek
- `EntryPoint` – Belépési pont típus és ár
- `Scenario` – Bullish/Bearish/Sideways forgatókönyv
- `RiskAssessment` – Kockázatkezelési adatok
- `AnalysisReport` – Teljes elemzési riport

### `app/core/image_analyzer.py`
Ollama Python SDK-n keresztül kommunikál a LLaVA modellel. A képet Base64-be kódolja és egy részletes magyar nyelvű prompttal küldi el. Hibakezelés: ha Ollama nem elérhető, visszaadja a hibaüzenetet (nem dob exception-t).

### `app/core/data_analyzer.py`
Összehangolja az összes algoritmikus elemzőt egy `dict`-be. Sorban hívja:
1. `TechnicalIndicators.calculate()`
2. `PatternDetector.detect()`
3. `FibonacciCalculator.calculate()`
4. `SupportResistanceDetector.detect()`

### `app/core/report_generator.py`
A nyers elemzési adatokból összeállítja a végleges `AnalysisReport`-ot:
- `ScenarioBuilder.build()` – 3 forgatókönyv generálása
- `RiskManager.calculate()` – Kockázatkezelési adatok (a legjobb bullish forgatókönyvhöz)
- `_calculate_confidence()` – Megbízhatóság score (0-95%)
- `_build_summary()` – Magyar nyelvű összefoglaló szöveg

### `app/core/analyzer.py`
Fő orchestrátor. 3 nyilvános async metódus:
- `analyze_image()` – Csak AI képelemzés
- `analyze_symbol()` – Csak OHLCV + technikai elemzés
- `analyze_combined()` – Mindkettő együtt

---

## Technikai Indikátorok (`app/indicators/technical.py`)

| Indikátor | Paraméterek | Outputok |
|-----------|-------------|----------|
| RSI | length=14 | érték, signal (oversold/neutral/overbought) |
| MACD | 12/26/9 | macd, signal, histogram, crossover |
| Bollinger Bands | length=20, std=2 | upper, middle, lower, squeeze |
| EMA | 9, 21, 50, 200 | értékek |
| SMA | 50, 200 | értékek, golden/death cross |
| ATR | length=14 | érték |
| Stochastic RSI | length=14 | %K, %D |
| Volume | rolling(20) | above_average flag |

---

## Chart Minta Detektálás (`app/indicators/patterns.py`)

Pivot pont alapú algoritmus (`window=5`). Detektált minták:

| Minta | Irány | Konfidencia |
|-------|-------|-------------|
| Head & Shoulders | bearish | 65% |
| Inverse Head & Shoulders | bullish | 65% |
| Double Top | bearish | 70% |
| Double Bottom | bullish | 70% |
| Symmetrical Triangle | neutral | 60% |
| Descending Triangle | bearish | 65% |
| Ascending Triangle | bullish | 65% |
| Bull Flag | bullish | 60% |
| Bear Flag | bearish | 60% |
| Rising Wedge | bearish | 58% |
| Falling Wedge | bullish | 58% |

---

## Fibonacci Szintek (`app/indicators/fibonacci.py`)

Az utolsó 50 gyertya swing high és swing low értékei alapján:

**Retracement szintek:** 23.6%, 38.2%, 50.0%, 61.8%, 78.6%

**Extension szintek:** 127.2%, 161.8%, 261.8%

---

## Support / Resistance Detektálás (`app/indicators/support_resistance.py`)

1. Pivot high-ok és low-ok keresése (`window=5`)
2. 1.5%-os toleranciával klaszterezés
3. Aktuális ár alatti szintek → support, feletti szintek → resistance
4. Erősség: érintések száma / 5 (max 1.0)
5. Max 5-5 szint visszaadva, távolság szerint rendezve

---

## Forgatókönyv Builder (`app/scenarios/scenario_builder.py`)

### Scoring rendszer

Pontszám számítás súlyokkal:

| Signal | Súly |
|--------|------|
| MACD bullish crossover | +15 |
| MACD bearish crossover | -15 |
| RSI oversold | +10 |
| RSI overbought | -10 |
| Golden Cross | +20 |
| Death Cross | -20 |
| Volume above average | +5 |
| Price above EMA50 | +8 |
| Price below EMA50 | -8 |
| Stoch oversold (<20) | +7 |
| Stoch overbought (>80) | -7 |
| Bullish pattern | +10 × confidence |
| Bearish pattern | -10 × confidence |

### Valószínűség számítás

A pontszámot [-80, +80] tartományra normalizálja, majd:
- Bullish score ≥ 0: bull_prob = 40 + normalized × 35
- Bearish score: bear_prob = 40 + |normalized| × 35
- Sideways: maradék (min. 5%)

---

## Kockázatkezelés (`app/strategies/`)

### Entry Calculator
- **breakout**: Legközelebbi resistance fölé 0.5%-kal
- **pullback**: EMA21-hez való visszatérés
- **reversal**: RSI oversold/overbought bouncehoz
- **market**: Ha nincs más signal

### Stop Loss Calculator
- **ATR-alapú**: entry ± ATR × 1.5
- **Structure-alapú**: Support/resistance szint ± 0.2%
- **Fallback**: entry × (1 ± 2%)

### Take Profit Calculator
- **TP1**: 1:1 R:R arány
- **TP2**: 1:2 R:R arány
- **TP3**: 1:3 R:R arány
- Fibonacci extension override, ha rendelkezésre áll

### Risk Manager
```
risk_amount = account_balance × (risk_percent / 100)
position_size = risk_amount / sl_distance
rr_ratio = reward / sl_distance
```

---

## Piaci Adatok (`app/market_data/`)

### BinanceProvider
- ccxt async library
- `fetch_ohlcv(symbol, timeframe, limit=300)`
- Automatikus fallback CoinGecko-ra hiba esetén
- Opcionális API key (magasabb rate limithez)

### CoinGeckoProvider
- httpx async HTTP kliens
- Szimbólum mapping: BTC/USDT → bitcoin stb.
- Timeframe → days mapping: 15m=1, 4h=30, 1d=365
- Opcionális Pro API key

---

## API Referencia

### `GET /api/v1/health`

```json
{
  "status": "ok",
  "ollama_connected": true,
  "model": "llava:13b"
}
```

### `POST /api/v1/analyze/symbol`

**Kérés:**
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "4h",
  "risk_percent": 2.0,
  "account_balance": 10000.0
}
```

**Válasz:** `AnalysisReport` (lásd models.py)

### `POST /api/v1/analyze/image`

**Kérés:** `multipart/form-data`
- `file`: PNG/JPEG/WebP kép
- `timeframe`: string (default: "4h")
- `risk_percent`: float (default: 2.0)

### `POST /api/v1/analyze/combined`

**Kérés:** `multipart/form-data`
- `file`: chart kép
- `symbol`: string
- `timeframe`: string
- `risk_percent`: float
- `account_balance`: float

---

## Telepítés és Üzemeltetés

### Fejlesztői módban

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8100
```

### Docker

```bash
docker build -t labot-chart-analyzer .
docker run -p 8100:8100 -e OLLAMA_HOST=http://host.docker.internal:11434 labot-chart-analyzer
```

### Docker Compose (ajánlott)

```bash
docker-compose up -d
# Ollama model letöltése (első alkalommal):
docker exec labot-ollama ollama pull llava:13b
```

### GPU támogatás

A `docker-compose.yml`-ben kommenteld ki a GPU részt:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

---

## Tesztelés

```bash
# Összes teszt
python -m pytest tests/ -v

# Egy modul
python -m pytest tests/test_indicators.py -v

# Coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Teszt modulok

| Fájl | Lefed |
|------|-------|
| `test_indicators.py` | TechnicalIndicators, FibonacciCalculator, SupportResistanceDetector |
| `test_strategies.py` | EntryCalculator, StopLossCalculator, TakeProfitCalculator, RiskManager |
| `test_analyzer.py` | ChartAnalyzer (mock-olt adatokkal) |
| `test_api.py` | FastAPI végpontok (mock-olt analyzer-rel) |

---

## Integráció LaBot.Api-val

A .NET backend a következő módon hívhatja:

```csharp
// DI regisztráció
services.AddHttpClient("ChartAnalyzer", client => {
    client.BaseAddress = new Uri(configuration["ChartAnalyzer:BaseUrl"]);
});

// Használat
var client = httpClientFactory.CreateClient("ChartAnalyzer");
var response = await client.PostAsJsonAsync("/api/v1/analyze/symbol", new {
    symbol = request.Symbol,
    timeframe = request.Timeframe,
    risk_percent = request.RiskPercent,
    account_balance = request.AccountBalance
});
var report = await response.Content.ReadFromJsonAsync<ChartAnalysisReport>();
```

### appsettings.json

```json
{
  "ChartAnalyzer": {
    "BaseUrl": "http://chart-analyzer:8100"
  }
}
```

---

## Ismert Korlátok

1. **Kép elemzés** – Pontossága függ a LLaVA modell minőségétől és a kép felbontásától
2. **Pattern detection** – Algoritmikus megközelítés, nem 100%-os pontosság
3. **CoinGecko fallback** – Korlátozott OHLCV adatok (nincs valódi timeframe szűrés ingyenes API-val)
4. **Stochastic RSI** – Rövid adatsoroknál nem számítható ki
5. **Golden/Death Cross** – 200 gyertyánál rövidebb adatsoron nem detektálható
