# pip install streamlit yfinance pandas plotly

import streamlit as st
import yfinance as yf
import pandas as pd
import math

# === Settings ===
CALL_TICKER = 'SPY240117C00550000'  # SPY Jan 17, 2026 $550 Call
ENTRY_PRICE = 44.78  # Your original cost basis

# === Data Fetching ===
def fetch_data():
    try:
        spy_price = yf.Ticker("SPY").history(period="1d")["Close"].dropna().iloc[-1]
    except Exception:
        spy_price = float("nan")
        st.error("❌ Failed to fetch SPY price.")

    try:
        vix_value = yf.Ticker("^VIX").history(period="1d")["Close"].dropna().iloc[-1]
    except Exception:
        vix_value = float("nan")
        st.error("❌ Failed to fetch VIX value.")

    try:
        call_hist = yf.Ticker(CALL_TICKER).history(period="5d")
        closes = call_hist["Close"].dropna()

        if len(closes) == 0:
            call_price = float("nan")
            is_fallback = False
        elif len(closes) == 1:
            call_price = closes.iloc[0]
            is_fallback = True
        else:
            call_price = closes.iloc[-1]
            is_fallback = False
    except Exception:
        call_price = float("nan")
        is_fallback = False
        st.error("❌ Failed to fetch SPY call price. Yahoo may be rate limiting.")

    return spy_price, vix_value, call_price, is_fallback

# === Trade Logic ===
def check_trade(spy_price, vix_value, call_price):
    call_pct_change = (call_price - ENTRY_PRICE) / ENTRY_PRICE * 100

    if spy_price < 500 or vix_value > 25:
        return "🚨 EMERGENCY EXIT 🚨", call_pct_change
    elif spy_price >= 680:
        return "✅ SELL FULL POSITION", call_pct_change
    elif spy_price >= 640:
        return "✅ SELL/ROLL PROFITS", call_pct_change
    elif spy_price >= 600:
        return "✅ SELL PARTIAL (25-33%)", call_pct_change
    elif call_pct_change >= 50:
        return "✅ SELL PARTIAL (OPTION UP +50%)", call_pct_change
    elif call_pct_change <= -30:
        return "🚨 CUT LOSS 🚨", call_pct_change
    else:
        return "👍 HOLD - No action needed", call_pct_change

# === Streamlit App ===
st.set_page_config(page_title="SPY Call Trade Monitor", page_icon="📈", layout="centered")
st.title("SPY Call Monitoring Dashboard 🚀")
st.write("Live monitoring for your SPY Jan 2026 $550c position")

with st.spinner("Fetching live data..."):
    spy_price, vix_value, call_price, is_fallback = fetch_data()

# Check if data is usable
if math.isnan(call_price):
    st.warning("⚠️ Could not fetch recent price for the SPY call option.")
    call_pct_change = 0
    action = "❌ Cannot make recommendation without option price"
else:
    if is_fallback:
        st.info("ℹ️ Using previous day's close for SPY call price.")
    action, call_pct_change = check_trade(spy_price, vix_value, call_price)

# Show Metrics
st.metric("SPY Spot Price", f"${spy_price:.2f}")
st.metric("VIX (Volatility Index)", f"{vix_value:.2f}")
st.metric("Your SPY Call Price", f"${call_price:.2f}", delta=f"{call_pct_change:.1f}% vs entry")

# Recommendation
st.header("🔗 Action Recommendation")
st.success(action) if "✅" in action or "👍" in action else st.error(action)

st.caption("⏱️ Refresh manually (hit R or refresh browser tab)")
st.markdown("---")
st.caption("Built by ChatGPT + You | Trading smarter, not harder. 🚀")
