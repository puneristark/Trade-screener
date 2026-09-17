import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Revarda & SaneBoon Screener", layout="wide")

# --- PIN SECURITY LOCK ---
APP_PIN = "7890"

st.sidebar.title("🔒 Security Access")
entered_pin = st.sidebar.text_input("Enter Access PIN", type="password")

if entered_pin != APP_PIN:
    st.warning("⚠️ Access Restricted. Enter PIN in sidebar.")
    st.stop()

st.title("🎯 Trade Execution & Setup Scanner")

# --- INTERMARKET MACRO BAROMETER ---
st.markdown("### 🌐 Intermarket Macro Barometer")

@st.cache_data(ttl=300)
def fetch_group_data(symbols_dict):
    data = []
    tickers = " ".join(symbols_dict.values())
    try:
        df = yf.download(tickers, period="2d", group_by='ticker', progress=False)
        for label, sym in symbols_dict.items():
            try:
                if len(symbols_dict) == 1:
                    close_series = df['Close']
                else:
                    close_series = df[sym]['Close']
                latest = float(close_series.dropna().iloc[-1])
                prev = float(close_series.dropna().iloc[-2]) if len(close_series.dropna()) >= 2 else latest
                chg = ((latest - prev) / prev) * 100 if prev != 0 else 0.0
                data.append({"Instrument": label, "Price": round(latest, 2), "Change %": f"{chg:+.2f}%"})
            except Exception:
                data.append({"Instrument": label, "Price": "N/A", "Change %": "--"})
    except Exception:
        for label in symbols_dict.keys():
            data.append({"Instrument": label, "Price": "N/A", "Change %": "--"})
    return pd.DataFrame(data)

macro_barometer = {
    "DXY Index": "DX-Y.NYB",
    "Gold (Spot)": "GC=F",
    "USD / INR": "USDINR=X"
}
macro_df = fetch_group_data(macro_barometer)

m1, m2, m3 = st.columns(3)
for idx, row in macro_df.iterrows():
    cols = [m1, m2, m3]
    val_prefix = "$" if "Gold" in row["Instrument"] else "₹" if "INR" in row["Instrument"] else ""
    cols[idx].metric(
        row["Instrument"],
        f"{val_prefix}{row['Price']}" if row['Price'] != "N/A" else "--",
        row["Change %"]
    )

st.markdown("---")

# --- TECHNICAL SCANNER ENGINE ---
st.markdown("### ⚡ Live Strategy Scans")

SCAN_UNIVERSE = {
    # Auto & Mobility
    "Eicher Motors": "EICHERMOT.NS", "Hero Moto": "HEROMOTOCO.NS", "Ashok Leyland": "ASHOKLEY.NS",
    "Tata Motors": "TATAMOTORS.NS", "TVS Motor": "TVSMOTOR.NS", "Maruti": "MARUTI.NS", "M&M": "M&M.NS",
    # Banking & Financials
    "HDFC Bank": "HDFCBANK.NS", "ICICI Bank": "ICICIBANK.NS", "Kotak Bank": "KOTAKBANK.NS",
    "IndusInd": "INDUSINDBK.NS", "SBI": "SBIN.NS", "Shriram Fin": "SHRIRAMFIN.NS",
    "Bajaj Finance": "BAJFINANCE.NS", "Axis Bank": "AXISBANK.NS", "M&M Fin": "M&MFIN.NS",
    "Motilal Oswal": "MOTILALOFS.NS", "BSE": "BSE.NS", "LIC": "LICI.NS", "ICICI Lombard": "ICICIGI.NS",
    # Energy, Power & Metals
    "JSW Energy": "JSWENERGY.NS", "ONGC": "ONGC.NS", "HPCL": "HINDPETRO.NS", "BPCL": "BPCL.NS",
    "Reliance": "RELIANCE.NS", "NTPC": "NTPC.NS", "Power Grid": "POWERGRID.NS", "Tata Power": "TATAPOWER.NS",
    "Jindal Steel": "JINDALSTEL.NS", "JSW Steel": "JSWSTEEL.NS", "Hindalco": "HINDALCO.NS", "Tata Steel": "TATASTEEL.NS",
    # IT, FMCG, Healthcare & Infra
    "TCS": "TCS.NS", "Infosys": "INFY.NS", "HCL Tech": "HCLTECH.NS", "Wipro": "WIPRO.NS", "Tech M": "TECHM.NS",
    "ITC": "ITC.NS", "HUL": "HINDUNILVR.NS", "Tata Cons": "TATACONSUM.NS", "L&T": "LT.NS",
    "Trent": "TRENT.NS", "UltraTech": "ULTRACEMCO.NS", "Asian Paints": "ASIANPAINT.NS",
    "Adani Ent": "ADANIENT.NS", "Airtel": "BHARTIARTL.NS", "Indus Towers": "INDUSTOWER.NS",
    "Cipla": "CIPLA.NS", "Dr Reddy": "DRREDDY.NS", "Sun Pharma": "SUNPHARMA.NS", "Titan": "TITAN.NS",
    # Commodities & Crypto
    "Crude Oil": "CL=F", "Silver": "SI=F", "Copper": "HG=F", "Natural Gas": "NG=F",
    "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"
}

@st.cache_data(ttl=600)
def calculate_setups(universe):
    revarda_hits = []
    saneboon_hits = []
    
    tickers_str = " ".join(universe.values())
    try:
        raw = yf.download(tickers_str, period="60d", interval="1d", group_by="ticker", progress=False)
    except Exception:
        return [], []

    for name, sym in universe.items():
        try:
            df = raw[sym].dropna() if len(universe) > 1 else raw.dropna()
            if len(df) < 30:
                continue
            
            close = df['Close']
            volume = df['Volume']
            high = df['High']
            low = df['Low']

            # 1. RSI (14) & Signal (EMA 9 of RSI)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss + 1e-9)
            rsi = 100 - (100 / (1 + rs))
            rsi_sig = rsi.ewm(span=9, adjust=False).mean()

            # 2. WaveTrend Oscillator
            ap = (high + low + close) / 3
            esa = ap.ewm(span=10, adjust=False).mean()
            d = (ap - esa).abs().ewm(span=10, adjust=False).mean()
            ci = (ap - esa) / (0.015 * d + 1e-9)
            wt1 = ci.ewm(span=21, adjust=False).mean()
            wt2 = wt1.rolling(4).mean()

            # 3. VWMA (20)
            vwma = (close * volume).rolling(20).sum() / (volume.rolling(20).sum() + 1e-9)

            # 4. ROC (9)
            roc9 = ((close - close.shift(9)) / close.shift(9)) * 100

            # Latest Values
            last_c = close.iloc[-1]
            last_rsi, prev_rsi = rsi.iloc[-1], rsi.iloc[-2]
            last_rsig, prev_rsig = rsi_sig.iloc[-1], rsi_sig.iloc[-2]
            last_wt1, prev_wt1 = wt1.iloc[-1], wt1.iloc[-2]
            last_wt2, prev_wt2 = wt2.iloc[-1], wt2.iloc[-2]
            last_vwma = vwma.iloc[-1]
            last_roc = roc9.iloc[-1]

            # REVARDA CRITERIA (WaveTrend Crossover + RSI Signal Confirmation)
            if (prev_wt1 <= prev_wt2 and last_wt1 > last_wt2) and (last_rsi > last_rsig):
                revarda_hits.append({"Asset": name, "Bias": "🟢 Bullish", "Price": round(last_c, 2), "RSI": round(last_rsi, 1), "WT1": round(last_wt1, 1)})
            elif (prev_wt1 >= prev_wt2 and last_wt1 < last_wt2) and (last_rsi < last_rsig):
                revarda_hits.append({"Asset": name, "Bias": "🔴 Bearish", "Price": round(last_c, 2), "RSI": round(last_rsi, 1), "WT1": round(last_wt1, 1)})

            # SANEBOON CRITERIA (Spot vs VWMA + ROC 9 Direction)
            if (last_c > last_vwma) and (last_roc > 0) and (last_rsi > 50):
                saneboon_hits.append({"Asset": name, "Bias": "🟢 Long Confluence", "Price": round(last_c, 2), "VWMA": round(last_vwma, 2), "ROC(9)": f"{last_roc:+.1f}%"})
            elif (last_c < last_vwma) and (last_roc < 0) and (last_rsi < 50):
                saneboon_hits.append({"Asset": name, "Bias": "🔴 Short Confluence", "Price": round(last_c, 2), "VWMA": round(last_vwma, 2), "ROC(9)": f"{last_roc:+.1f}%"})

        except Exception:
            continue

    return revarda_hits, saneboon_hits

rev_hits, sane_hits = calculate_setups(SCAN_UNIVERSE)

col1, col2 = st.columns(2)
with col1:
    st.subheader("⚡ Revarda Setups")
    if rev_hits:
        st.dataframe(pd.DataFrame(rev_hits), use_container_width=True, hide_index=True)
    else:
        st.info("No active Revarda crossovers today.")

with col2:
    st.subheader("🌊 SaneBoon Setups")
    if sane_hits:
        st.dataframe(pd.DataFrame(sane_hits), use_container_width=True, hide_index=True)
    else:
        st.info("No active SaneBoon confluence triggers detected.")

st.markdown("---")

# --- MULTI-ASSET MONITORING TABS ---
st.markdown("### 📋 Watchlist Monitor")
t1, t2, t3, t4 = st.tabs(["📈 F&O Stocks", "🛢️ Commodities", "💱 Currencies", "⚡ Crypto"])

with t1:
    fno_symbols = {
        "Eicher Motors": "EICHERMOT.NS", "Hero Moto": "HEROMOTOCO.NS", "Ashok Leyland": "ASHOKLEY.NS",
        "Tata Motors": "TATAMOTORS.NS", "TVS Motor": "TVSMOTOR.NS", "Maruti": "MARUTI.NS", "M&M": "M&M.NS",
        "HDFC Bank": "HDFCBANK.NS", "ICICI Bank": "ICICIBANK.NS", "Kotak Bank": "KOTAKBANK.NS",
        "IndusInd": "INDUSINDBK.NS", "SBI": "SBIN.NS", "Shriram Fin": "SHRIRAMFIN.NS",
        "Bajaj Finance": "BAJFINANCE.NS", "Axis Bank": "AXISBANK.NS", "M&M Fin": "M&MFIN.NS",
        "Motilal Oswal": "MOTILALOFS.NS", "BSE": "BSE.NS", "LIC": "LICI.NS", "ICICI Lombard": "ICICIGI.NS",
        "JSW Energy": "JSWENERGY.NS", "ONGC": "ONGC.NS", "HPCL": "HINDPETRO.NS", "BPCL": "BPCL.NS",
        "Reliance": "RELIANCE.NS", "NTPC": "NTPC.NS", "Power Grid": "POWERGRID.NS", "Tata Power": "TATAPOWER.NS",
        "Jindal Steel": "JINDALSTEL.NS", "JSW Steel": "JSWSTEEL.NS", "Hindalco": "HINDALCO.NS", "Tata Steel": "TATASTEEL.NS",
        "TCS": "TCS.NS", "Infosys": "INFY.NS", "HCL Tech": "HCLTECH.NS", "Wipro": "WIPRO.NS", "Tech M": "TECHM.NS",
        "ITC": "ITC.NS", "HUL": "HINDUNILVR.NS", "Tata Cons": "TATACONSUM.NS", "L&T": "LT.NS",
        "Trent": "TRENT.NS", "UltraTech": "ULTRACEMCO.NS", "Asian Paints": "ASIANPAINT.NS",
        "Adani Ent": "ADANIENT.NS", "Airtel": "BHARTIARTL.NS", "Indus Towers": "INDUSTOWER.NS",
        "Cipla": "CIPLA.NS", "Dr Reddy": "DRREDDY.NS", "Sun Pharma": "SUNPHARMA.NS", "Titan": "TITAN.NS"
    }
    st.dataframe(fetch_group_data(fno_symbols), use_container_width=True, hide_index=True)

with t2:
    comm_symbols = {
        "Crude Oil": "CL=F", "Silver": "SI=F", "Copper": "HG=F",
        "Natural Gas": "NG=F", "Zinc": "ZNC=F", "Nickel": "NICKEL=F", "Aluminium": "ALI=F"
    }
    st.dataframe(fetch_group_data(comm_symbols), use_container_width=True, hide_index=True)

with t3:
    curr_symbols = {
        "USD/INR": "USDINR=X", "DXY Index": "DX-Y.NYB", "Gold/Silver": "XAUXAG=X",
        "GBP/INR": "GBPINR=X", "GBP/USD": "GBPUSD=X", "EUR/INR": "EURINR=X",
        "EUR/USD": "EURUSD=X", "JPY/INR": "JPYINR=X", "USD/JPY": "JPY=X"
    }
    st.dataframe(fetch_group_data(curr_symbols), use_container_width=True, hide_index=True)

with t4:
    crypto_symbols = {
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD",
        "Ripple (XRP)": "XRP-USD", "Cardano": "ADA-USD", "Litecoin": "LTC-USD",
        "Bitcoin Cash": "BCH-USD", "Binance Coin": "BNB-USD", "Polygon (POL)": "POL-USD"
    }
    st.dataframe(fetch_group_data(crypto_symbols), use_container_width=True, hide_index=True)
