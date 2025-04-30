# Install needed packages first if you haven't:
# pip install streamlit yfinance pandas plotly

import streamlit as st
import yfinance as yf
import pandas as pd

# === Settings ===
CALL_TICKER = 'SPY240117C00550000'  # SPY Jan 17, 2026 $550 Call
ENTRY_PRICE = 44.78  # Your original cost basis

# === Fetch Live Data ===
def fetch_data():
    try:
        spy = yf.Ticker("SPY")
        spy_price = spy.history(period="1d")["Close"].dropna().iloc[-1]
    except Exception as e:
        try:
        # Pull last 2 closing prices for the call option
        hist = call.history(period="5d")
        closes = hist["Close"].dropna()

        if len(closes) == 0:
            call_price = float("nan")
            is_fallback = False
        elif len(closes) == 1:
            call_price = closes.iloc[0]
            is_fallback = True
        else:
            call_price = closes.iloc[-1]
            is_fallback = False

    except Exception as e:
        call_price = float("nan")
        is_fallback = False
        st.error("❌ Failed to fetch call option price. Possibly rate limited.")

        call = yf.Ticker(CALL_TICKER)
        hist = call.history(period="5d")
        closes = hist["Close"].dropna()
        if len(closes) == 0:
            call_price = float("nan")
            is_fallback = False
        elif len(closes) == 1:
            call_price = closes.iloc[0]
            is_fallback = True
        else:
            call_price = closes.iloc[-1]
            is_fallback = False
    except Exception as e:
        call_price = float("nan")
        is_fallback = False
        st.error("❌ Failed to fetch call option price. Possibly rate limited.")

    return spy_price, vix_value, call_price, is_fallback
    else:
        call_price = closes.iloc[-1]
        is_fallback = False

    return spy_price, vix_value, call_price, is_fallback

# === Trading Logic ===
def check_trade(spy_price, vix_value, call_price):
    call_pct_change = (call_price - ENTRY_PRICE) / ENTRY_PRICE * 100

    if spy_price < 500 or vix_value > 25:
        action = "🚨 EMERGENCY EXIT 🚨"
    elif spy_price >= 680:
        action = "✅ SELL FULL POSITION"
    elif spy_price >= 640:
        action = "✅ SELL/ROLL PROFITS"
    elif spy_price >= 600:
        action = "✅ SELL PARTIAL (25-33%)"
    elif call_pct_change >= 50:
        action = "✅ SELL PARTIAL (OPTION UP +50%)"
    elif call_pct_change <= -30:
        action = "🚨 CUT LOSS 🚨"
    else:
        action = "👍 HOLD - No action needed"

    return action, call_pct_change

# === Streamlit Web App ===
st.set_page_config(page_title="SPY Call Trade Monitor", page_icon="📈", layout="centered")
st.title("SPY Call Monitoring Dashboard 🚀")

st.write("Live monitoring for your SPY Jan 2026 $550c position")

import math

with st.spinner('Fetching live data...'):
    spy_price, vix_value, call_price, is_fallback = fetch_data()

if math.isnan(call_price):
    st.warning("⚠️ Could not fetch recent price data for the SPY call. Data may be delayed or unavailable.")
else:
    if is_fallback:
        st.info("ℹ️ Using previous day's close for SPY call price.")

    action, call_pct_change = check_trade(spy_price, vix_value, call_price)

# Show metrics
st.metric(label="SPY Spot Price", value=f"${spy_price:.2f}")
st.metric(label="VIX (Volatility Index)", value=f"{vix_value:.2f}")
st.metric(label="Your SPY Call Price", value=f"${call_price:.2f}", delta=f"{call_pct_change:.1f}% vs entry")

st.header("🔗 Action Recommendation")
st.success(action) if "✅" in action else st.error(action)

st.caption("\u23f0 Data auto-refreshes manually (hit Rerun or refresh browser)")

# Future improvements placeholder
# if st.button("Auto-Refresh Every X Minutes"): 
#     (coming later)

# Footer
st.markdown("---")
st.caption("Built by ChatGPT + You | Trading smarter, not harder. 🚀")

