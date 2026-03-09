"""Streamlit dashboard for LaBot Chart Analyzer."""
from __future__ import annotations

import io
import json

import httpx
import plotly.graph_objects as go
import streamlit as st

API_BASE = "http://localhost:8100/api/v1"

st.set_page_config(
    page_title="LaBot Chart Analyzer",
    page_icon="📊",
    layout="wide",
)

st.title("📊 LaBot Chart Analyzer")
st.caption("AI-alapú kriptovaluta technikai elemzés")

tab1, tab2, tab3 = st.tabs(["🖼️ Kép Elemzés", "📈 Szimbólum Elemzés", "🔀 Kombinált"])


def _display_report(report: dict) -> None:
    """Render an analysis report in Streamlit."""
    st.success(f"✅ Elemzés kész: {report.get('symbol')} ({report.get('timeframe')})")
    st.write(f"**Összefoglaló:** {report.get('summary', '')}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Megbízhatóság", f"{report.get('confidence', 0):.0f}%")
    ind = report.get("indicators", {})
    col2.metric("RSI", f"{ind.get('rsi', 'N/A')}")
    col3.metric("Jelenlegi ár", f"{ind.get('current_price', 'N/A')}")

    st.subheader("📊 Forgatókönyvek")
    for scenario in report.get("scenarios", []):
        direction_label = {"bullish": "Emelkedő", "bearish": "Csökkenő", "sideways": "Oldalazó"}.get(
            scenario["direction"], scenario["direction"]
        )
        with st.expander(f"{scenario['emoji']} {direction_label} – {scenario['probability']:.0f}%"):
            if scenario.get("entry"):
                st.write(f"**Entry:** {scenario['entry']['price']:.4f} ({scenario['entry']['type']})")
            if scenario.get("stop_loss"):
                st.write(f"**Stop Loss:** {scenario['stop_loss']:.4f}")
            if scenario.get("tp1"):
                st.write(f"**TP1:** {scenario['tp1']:.4f} | **TP2:** {scenario.get('tp2', 'N/A')} | **TP3:** {scenario.get('tp3', 'N/A')}")
            if scenario.get("rr_ratio"):
                st.write(f"**R:R arány:** 1:{scenario['rr_ratio']:.2f}")
            if scenario.get("actions"):
                st.write("**Teendők:**")
                for action in scenario["actions"]:
                    st.write(f"- {action}")

    if report.get("patterns"):
        st.subheader("🔍 Felismert minták")
        for pat in report["patterns"]:
            st.write(f"- **{pat['name']}** ({pat['direction']}) – {pat['confidence']*100:.0f}%")

    if report.get("ai_interpretation"):
        st.subheader("🤖 AI értelmezés (LLaVA)")
        st.info(report["ai_interpretation"])

    with st.expander("📋 Nyers JSON"):
        st.json(report)


# ── Tab 1: Image Analysis ─────────────────────────────────────────────────────
with tab1:
    st.header("Kép alapú chart elemzés")
    uploaded_file = st.file_uploader("Tölts fel egy chart képet", type=["png", "jpg", "jpeg", "webp"])
    timeframe_img = st.selectbox("Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=3, key="tf_img")
    risk_img = st.number_input("Kockázat %", min_value=0.1, max_value=10.0, value=2.0, step=0.1, key="risk_img")

    if uploaded_file and st.button("Elemzés indítása", key="btn_img"):
        with st.spinner("AI elemzés folyamatban..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            params = {"timeframe": timeframe_img, "risk_percent": risk_img}
            try:
                resp = httpx.post(f"{API_BASE}/analyze/image", files=files, params=params, timeout=120)
                resp.raise_for_status()
                report = resp.json()
                _display_report(report)
            except Exception as e:
                st.error(f"Hiba: {e}")

# ── Tab 2: Symbol Analysis ────────────────────────────────────────────────────
with tab2:
    st.header("Szimbólum alapú elemzés")
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Szimbólum", value="BTC/USDT")
        timeframe_sym = st.selectbox("Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=3, key="tf_sym")
    with col2:
        risk_sym = st.number_input("Kockázat %", min_value=0.1, max_value=10.0, value=2.0, step=0.1, key="risk_sym")
        balance = st.number_input("Számla egyenleg ($)", min_value=100.0, value=10000.0, step=100.0)

    if st.button("Elemzés indítása", key="btn_sym"):
        with st.spinner(f"Adatok letöltése és elemzés: {symbol}..."):
            payload = {
                "symbol": symbol,
                "timeframe": timeframe_sym,
                "risk_percent": risk_sym,
                "account_balance": balance,
            }
            try:
                resp = httpx.post(f"{API_BASE}/analyze/symbol", json=payload, timeout=60)
                resp.raise_for_status()
                report = resp.json()
                _display_report(report)
            except Exception as e:
                st.error(f"Hiba: {e}")

# ── Tab 3: Combined ───────────────────────────────────────────────────────────
with tab3:
    st.header("Kombinált elemzés (kép + élő adat)")
    comb_file = st.file_uploader("Chart kép", type=["png", "jpg", "jpeg", "webp"], key="comb_img")
    col1, col2 = st.columns(2)
    with col1:
        comb_symbol = st.text_input("Szimbólum", value="BTC/USDT", key="comb_symbol")
        comb_tf = st.selectbox("Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=3, key="comb_tf")
    with col2:
        comb_risk = st.number_input("Kockázat %", min_value=0.1, max_value=10.0, value=2.0, key="comb_risk")
        comb_balance = st.number_input("Számla ($)", min_value=100.0, value=10000.0, key="comb_balance")

    if comb_file and st.button("Kombinált elemzés", key="btn_comb"):
        with st.spinner("Kombinált elemzés..."):
            files = {"file": (comb_file.name, comb_file.getvalue(), comb_file.type)}
            data = {
                "symbol": comb_symbol,
                "timeframe": comb_tf,
                "risk_percent": str(comb_risk),
                "account_balance": str(comb_balance),
            }
            try:
                resp = httpx.post(f"{API_BASE}/analyze/combined", files=files, data=data, timeout=120)
                resp.raise_for_status()
                _display_report(resp.json())
            except Exception as e:
                st.error(f"Hiba: {e}")
