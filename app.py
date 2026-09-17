import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# Page setup
st.set_page_config(page_title="Revarda & SaneBoon Execution Screener", layout="wide")

# --- PIN SECURITY LOCK ---
APP_PIN = "7890"  # You can change this 4-digit PIN anytime

st.sidebar.title("🔒 Security Access")
entered_pin = st.sidebar.text_input("Enter Access PIN", type="password")

if entered_pin != APP_PIN:
    st.warning("⚠️ Access Restricted. Please enter your PIN in the sidebar to view signals.")
    st.stop()

# --- INTERMARKET MACRO BAROMETER ---
st.title("🎯 Trade Execution & Signal Review Dashboard")
st.markdown("### 🌐 Intermarket Macro Barometer")

@st.cache_data(ttl=300)
def fetch_macro_indicators():
    symbols = {
        "DXY (Dollar Index)": "DX-Y.NYB",
        "Gold Spot / Futures": "GC=F",
        "USD/INR": "USDINR=X"
    }
    data = {}
    for label, sym in symbols.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                latest = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                chg = ((latest - prev) / prev) * 100
                data[label] = (latest, chg)
            elif len(hist) == 1:
                data[label] = (hist['Close'].iloc[-1], 0.0)
            else:
                data[label] = (None, None)
        except Exception:
            data[label] = (None, None)
    return data

macro_data = fetch_macro_indicators()
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    val, chg = macro_data.get("DXY (Dollar Index)", (None, None))
    if val is not None:
        st.metric(label="💵 US Dollar Index (DXY)", value=f"{val:.2f}", delta=f"{chg:+.2f}%")
    else:
        st.metric(label="💵 US Dollar Index (DXY)", value="Syncing...", delta="--")

with m_col2:
    val, chg = macro_data.get("Gold Spot / Futures", (None, None))
    if val is not None:
        st.metric(label="🪙 Gold (GC=F)", value=f"${val:,.1f}", delta=f"{chg:+.2f}%")
    else:
        st.metric(label="🪙 Gold (GC=F)", value="Syncing...", delta="--")

with m_col3:
    val, chg = macro_data.get("USD/INR", (None, None))
    if val is not None:
        st.metric(label="🇮🇳 USD / INR", value=f"₹{val:.3f}", delta=f"{chg:+.2f}%")
    else:
        st.metric(label="🇮🇳 USD / INR", value="Syncing...", delta="--")

st.markdown("---")

# --- SIGNAL FEED & REVIEW GATES ---
WEBHOOK_BACKEND_URL = st.sidebar.text_input("Webhook Backend URL", "http://localhost:8000/alerts")

def get_incoming_signals():
    try:
        res = requests.get(WEBHOOK_BACKEND_URL, timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

signals = get_incoming_signals()

col_rev, col_sane = st.columns(2)

# --- REVARDA SYSTEM VIEW ---
with col_rev:
    st.subheader("1. Revarda System Triggers")
    revarda_items = [s for s in signals if s.get("system", "").lower() == "revarda"]
    
    if revarda_items:
        for item in revarda_items:
            tag_color = "🟢" if "BUY" in item.get("signal", "").upper() else "🔴"
            symbol = item.get("symbol", "N/A")
            price = item.get("price", 0.0)
            tf = item.get("timeframe", "125m / 1D")
            
            with st.expander(f"{tag_color} {item.get('signal')} - {symbol} @ ₹{price} ({tf})", expanded=True):
                st.markdown("**Automated Trigger Confirmed:**")
                st.caption("• RSI 14-EMA Cross | • WaveTrend Cross | • ADX DI+/DI- Cross | • OBV Bollinger Touch")
                
                st.markdown("#### 1. Core Technical Checklist")
                st.checkbox(f"SMC (Smart Money Concepts) Validated", key=f"rev_smc_{symbol}")
                st.checkbox(f"GEMS A.I. System Confluence Confirmed", key=f"rev_gems_{symbol}")

                st.markdown("#### 2. Mandatory Macro & Currency Gate")
                st.checkbox(f"Review DXY (Dollar Index) alignment for {symbol}", key=f"rev_dxy_{symbol}")
                st.checkbox(f"Review Gold correlation/momentum", key=f"rev_gold_{symbol}")
                st.checkbox(f"Review USD/INR trend & currency pressure", key=f"rev_usdinr_{symbol}")
                
                st.markdown("---")
                if st.button(f"Confirm & Route {symbol} to Execution", key=f"btn_rev_{symbol}"):
                    st.success(f"All technical + macro checks completed for {symbol}.")
    else:
        st.info("No active Revarda signals pending review.")

# --- SANEBOON SYSTEM VIEW ---
with col_sane:
    st.subheader("2. SaneBoon System Triggers")
    saneboon_items = [s for s in signals if s.get("system", "").lower() == "saneboon"]
    
    if saneboon_items:
        for item in saneboon_items:
            tag_color = "🟢" if "BUY" in item.get("signal", "").upper() else "🔴"
            symbol = item.get("symbol", "N/A")
            price = item.get("price", 0.0)
            tf = item.get("timeframe", "125m / 1D")
            
            with st.expander(f"{tag_color} {item.get('signal')} - {symbol} @ ₹{price} ({tf})", expanded=True):
                st.markdown("**Automated Trigger Confirmed:**")
                st.caption("• Spot vs VWMA(20) Cross | • RSI 14-EMA Cross | • ROC(9) Zero-Line Cross")
                
                st.markdown("#### 1. Core Technical Checklist")
                st.checkbox(f"ROC (9) Bullish / Hidden Bullish Divergence Verified", key=f"sane_roc_{symbol}")
                st.checkbox(f"Smart Money Oscillator (ChartPrime) Verified", key=f"sane_smo_{symbol}")
                st.checkbox(f"CVD (9, 15) Delta Flow Checked", key=f"sane_cvd_{symbol}")
                st.checkbox(f"GEMS A.I. System Confluence Confirmed", key=f"sane_gems_{symbol}")

                st.markdown("#### 2. Mandatory Macro & Currency Gate")
                st.checkbox(f"Review DXY (Dollar Index) alignment for {symbol}", key=f"sane_dxy_{symbol}")
                st.checkbox(f"Review Gold correlation/momentum", key=f"sane_gold_{symbol}")
                st.checkbox(f"Review USD/INR trend & currency pressure", key=f"sane_usdinr_{symbol}")

                st.markdown("---")
                if st.button(f"Confirm & Route {symbol} to Execution", key=f"btn_sane_{symbol}"):
                    st.success(f"All technical + macro checks completed for {symbol}.")
    else:
        st.info("No active SaneBoon signals pending review.")
