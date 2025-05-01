# --- Requirements ---
# pip install streamlit yahooquery pandas

import streamlit as st
from yahooquery import Ticker
import pandas as pd
import math

# === Settings ===
CALL_TICKER = 'SPY240117C00550000'  # SPY Jan 17, 2026 $550 Call
ENTRY_PRICE = 44.78  # Cost basis for your call

# === Fetch Data Using yahooquery ===
def fetch_data():
    try:
        tickers = Ticker(["SPY", "^VIX", "SPY"])
        
        # Get latest SPY and VIX price
        hist = tickers.history(period="1d")
        spy_price = hist.loc[("SPY",), "close"].iloc[-1]
        vix_value = hist.loc[("^VIX",), "close"].iloc[-1]

        # Get the option chain
        chain = tickers.option_chain
        calls = chain.get("calls", [])

        # Search for your call contract
        call_data = next((c for c in calls if c["contractSymbol"] == CALL_TICKER), None)

        if call_data and "lastPrice" in call_data:
            call_price = call_data["lastPrice"]
            is_fallback = False
        else:
            call_price = float("nan")
            is_fallback = False

    except Exception as e:
        st.error(f"❌ Error during data fetch: {e}")
        spy_price = float("nan")
        vix_value = float("nan")
        call_price = float("nan")
        is_fallback = False

    return spy_price, vix_value, call_price, is_fallback

# === Trade Signal Logic ===
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

# === Streamlit App ===
st.set_page_config(page_title="SPY Call Monitor", page_icon="📈", layout="centered")
st.title("SPY Call Monitoring Dashboard 🚀")
st.write("Live monitoring for your SPY Jan 2026 $550c position")

with st.spinner("Fetching live data..."):
    spy_price, vix_value, call_price, is_fallback = fetch_data()

if math.isnan(call_price):
    st.error("❌ Failed to fetch SPY call price. Yahoo may be rate limiting or the symbol is incorrect.")
    st.warning("⚠️ Could not fetch recent price for the SPY call option.")
else:
    if is_fallback:
        st.info("ℹ️ Using fallback price for the SPY call.")

    action, call_pct_change = check_trade(spy_price, vix_value, call_price)

    st.metric(label="SPY Spot Price", value=f"${spy_price:.2f}")
    st.metric(label="VIX (Volatility Index)", value=f"{vix_value:.2f}")
    st.metric(label="Your SPY Call Price", value=f"${call_price:.2f}", delta=f"{call_pct_change:.1f}% vs entry")

    st.header("🔗 Action Recommendation")
    st.success(action) if "✅" in action else st.error(action)

st.caption("⏱️ Data refreshes manually. Click Rerun or refresh browser.")

st.markdown("---")
st.caption("Built by ChatGPT + You | Trading smarter, not harder. 🚀")
