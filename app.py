
import streamlit as st
import yfinance as yf
import requests
import pandas as pd

st.set_page_config(page_title="Revarda & SaneBoon Screener", layout="wide")
APP_PIN = "7890"

st.sidebar.title("🔒 Security Access")
entered_pin = st.sidebar.text_input("Enter Access PIN", type="password")

if entered_pin != APP_PIN:
    st.warning("⚠️ Access Restricted. Enter PIN.")
    st.stop()

st.title("🎯 Trade Execution Dashboard")

@st.cache_data(ttl=300)
def fetch_data(sym_dict):
    out = []
    tickers = " ".join(sym_dict.values())
    try:
        df = yf.download(tickers, period="2d", group_by="ticker", progress=False)
        for label, sym in sym_dict.items():
            try:
                s = df['Close'] if len(sym_dict) == 1 else df[sym]['Close']
                last = float(s.dropna().iloc[-1])
                prev = float(s.dropna().iloc[-2]) if len(s.dropna()) >= 2 else last
                chg = ((last - prev) / prev) * 100
                out.append({"Symbol": label, "Price": round(last, 2), "Change %": f"{chg:+.2f}%"})
            except Exception:
                out.append({"Symbol": label, "Price": "N/A", "Change %": "--"})
    except Exception:
        for label in sym_dict.keys():
            out.append({"Symbol": label, "Price": "N/A", "Change %": "--"})
    return pd.DataFrame(out)

st.markdown("### 🌐 Intermarket Macro Barometer")
macro = {"DXY Index": "DX-Y.NYB", "Gold": "GC=F", "USD/INR": "USDINR=X"}
m_df = fetch_data(macro)
c1, c2, c3 = st.columns(3)
for i, r in m_df.iterrows():
    [c1, c2, c3][i].metric(r["Symbol"], str(r["Price"]), r["Change %"])

st.markdown("---")
st.markdown("### 📋 Watchlists")
t1, t2, t3, t4 = st.tabs(["F&O Stocks", "Commodities", "Currencies", "Crypto"])

with t1:
    fno = {
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
    st.dataframe(fetch_data(fno), use_container_width=True, hide_index=True)

with t2:
    comm = {"Crude Oil": "CL=F", "Silver": "SI=F", "Copper": "HG=F", "Natural Gas": "NG=F", "Zinc": "ZNC=F", "Nickel": "NICKEL=F", "Aluminium": "ALI=F"}
    st.dataframe(fetch_data(comm), use_container_width=True, hide_index=True)

with t3:
    curr = {"USD/INR": "USDINR=X", "DXY": "DX-Y.NYB", "Gold/Silver": "XAUXAG=X", "GBP/INR": "GBPINR=X", "GBP/USD": "GBPUSD=X", "EUR/INR": "EURINR=X", "EUR/USD": "EURUSD=X", "JPY/INR": "JPYINR=X", "USD/JPY": "JPY=X"}
    st.dataframe(fetch_data(curr), use_container_width=True, hide_index=True)

with t4:
    crypto = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "XRP": "XRP-USD", "ADA": "ADA-USD", "LTC": "LTC-USD", "BCH": "BCH-USD", "BNB": "BNB-USD", "POL": "POL-USD"}
    st.dataframe(fetch_data(crypto), use_container_width=True, hide_index=True)
