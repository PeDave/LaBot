from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import pandas_ta as ta

from app.api.models import IndicatorSummary

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculates RSI, MACD, Bollinger Bands, EMAs, SMA, ATR, Stochastic RSI, Volume."""

    def calculate(self, df: pd.DataFrame) -> IndicatorSummary:
        if df is None or len(df) < 30:
            return IndicatorSummary()

        close = df["close"]
        volume = df["volume"] if "volume" in df.columns else None

        result = IndicatorSummary(current_price=float(close.iloc[-1]))

        # RSI
        try:
            rsi = ta.rsi(close, length=14)
            if rsi is not None and not rsi.empty:
                rsi_val = float(rsi.iloc[-1])
                result.rsi = rsi_val
                result.rsi_signal = (
                    "oversold" if rsi_val < 30 else "overbought" if rsi_val > 70 else "neutral"
                )
        except Exception as e:
            logger.debug("RSI error: %s", e)

        # MACD
        try:
            macd_df = ta.macd(close, fast=12, slow=26, signal=9)
            if macd_df is not None and not macd_df.empty:
                macd_col = [c for c in macd_df.columns if c.startswith("MACD_")]
                signal_col = [c for c in macd_df.columns if c.startswith("MACDs_")]
                hist_col = [c for c in macd_df.columns if c.startswith("MACDh_")]
                if macd_col:
                    result.macd = float(macd_df[macd_col[0]].iloc[-1])
                if signal_col:
                    result.macd_signal = float(macd_df[signal_col[0]].iloc[-1])
                if hist_col and len(macd_df) >= 2:
                    h_now = float(macd_df[hist_col[0]].iloc[-1])
                    h_prev = float(macd_df[hist_col[0]].iloc[-2])
                    result.macd_histogram = h_now
                    if h_prev < 0 < h_now:
                        result.macd_crossover = "bullish"
                    elif h_prev > 0 > h_now:
                        result.macd_crossover = "bearish"
        except Exception as e:
            logger.debug("MACD error: %s", e)

        # Bollinger Bands
        try:
            bb = ta.bbands(close, length=20, std=2)
            if bb is not None and not bb.empty:
                upper_col = [c for c in bb.columns if "BBU" in c]
                mid_col = [c for c in bb.columns if "BBM" in c]
                lower_col = [c for c in bb.columns if "BBL" in c]
                bw_col = [c for c in bb.columns if "BBB" in c]
                if upper_col:
                    result.bb_upper = float(bb[upper_col[0]].iloc[-1])
                if mid_col:
                    result.bb_middle = float(bb[mid_col[0]].iloc[-1])
                if lower_col:
                    result.bb_lower = float(bb[lower_col[0]].iloc[-1])
                if bw_col and len(bb) >= 20:
                    bw_series = bb[bw_col[0]].dropna()
                    if len(bw_series) >= 5:
                        result.bb_squeeze = float(bw_series.iloc[-1]) < float(bw_series.rolling(20).mean().iloc[-1]) * 0.5
        except Exception as e:
            logger.debug("Bollinger error: %s", e)

        # EMAs
        for period, attr in [(9, "ema_9"), (21, "ema_21"), (50, "ema_50"), (200, "ema_200")]:
            try:
                ema = ta.ema(close, length=period)
                if ema is not None and not ema.empty and not np.isnan(ema.iloc[-1]):
                    setattr(result, attr, float(ema.iloc[-1]))
            except Exception as e:
                logger.debug("EMA%d error: %s", period, e)

        # SMAs
        for period, attr in [(50, "sma_50"), (200, "sma_200")]:
            try:
                sma = ta.sma(close, length=period)
                if sma is not None and not sma.empty and not np.isnan(sma.iloc[-1]):
                    setattr(result, attr, float(sma.iloc[-1]))
            except Exception as e:
                logger.debug("SMA%d error: %s", period, e)

        # Golden / Death Cross (SMA50 vs SMA200)
        if result.sma_50 and result.sma_200:
            try:
                sma50 = ta.sma(close, length=50)
                sma200 = ta.sma(close, length=200)
                if sma50 is not None and sma200 is not None and len(sma50) >= 2 and len(sma200) >= 2:
                    prev50 = float(sma50.iloc[-2])
                    prev200 = float(sma200.iloc[-2])
                    curr50 = float(sma50.iloc[-1])
                    curr200 = float(sma200.iloc[-1])
                    if prev50 < prev200 and curr50 > curr200:
                        result.golden_cross = True
                    elif prev50 > prev200 and curr50 < curr200:
                        result.death_cross = True
            except Exception as e:
                logger.debug("Cross error: %s", e)

        # ATR
        try:
            atr = ta.atr(df["high"], df["low"], close, length=14)
            if atr is not None and not atr.empty and not np.isnan(atr.iloc[-1]):
                result.atr = float(atr.iloc[-1])
        except Exception as e:
            logger.debug("ATR error: %s", e)

        # Stochastic RSI
        try:
            stoch_rsi = ta.stochrsi(close, length=14)
            if stoch_rsi is not None and not stoch_rsi.empty:
                k_col = [c for c in stoch_rsi.columns if c.endswith("K")]
                d_col = [c for c in stoch_rsi.columns if c.endswith("D")]
                if k_col and not np.isnan(stoch_rsi[k_col[0]].iloc[-1]):
                    result.stoch_k = float(stoch_rsi[k_col[0]].iloc[-1])
                if d_col and not np.isnan(stoch_rsi[d_col[0]].iloc[-1]):
                    result.stoch_d = float(stoch_rsi[d_col[0]].iloc[-1])
        except Exception as e:
            logger.debug("StochRSI error: %s", e)

        # Volume
        if volume is not None:
            try:
                vol_mean = volume.rolling(20).mean().iloc[-1]
                result.volume_above_average = float(volume.iloc[-1]) > float(vol_mean)
            except Exception as e:
                logger.debug("Volume error: %s", e)

        return result
