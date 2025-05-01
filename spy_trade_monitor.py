# pip install streamlit yahooquery pandas

import streamlit as st
from yahooquery import Ticker
import pandas as pd
import time
import math
from datetime import datetime

# === Settings ===
CALL_TICKER = 'SPY240117C00550000'  # SPY Jan 17, 2026 $550 Call
ENTRY_PRICE = 44.78  # Your cost basis

st.set_page_config(page_title="SPY Call Trade Monitor", page_icon="📈", layout="centered")
st.title("SPY Call Monitoring Dashboard 🚀")
st.write("Live monitoring for your SPY Jan 2026 $550c position")

# === Helper Functions ===
def fetch_data():
    try:
        time.sleep(1.5)  # <== THROTTLE to prevent rate-limiting

        tickers = Ticker(["SPY", "^VIX", CALL_TICKER])

        spy_price = tickers["SPY"].price["SPY"]["regularMarketPrice"]
        vix_value = tickers["^VIX"].price["^VIX"]["regularMarketPrice"]

        opt_chain = tickers.get_options_data()
        call_row = opt_chain.loc[CALL_TICKER] if CALL_TICKER in opt_chain.index else None

        if call_row is not None:
            call_price = call_row["lastPrice"]
            is_fallback = False
        else:
            call_price = float("nan")
            is_fallback = False

        return spy_price, vix_value, call_price, is_fallback, None

    except Exception as e:
        return None, None, float("nan"), False, str(e)

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

# === App Logic ===
start_time = time.time()

with st.spinner("Fetching live data..."):
    spy_price, vix_value, call_price, is_fallback, error = fetch_data()

# === Handle data fetch errors ===
if error:
    st.error(f"❌ Error during data fetch: {error}")

# === Check for missing option price ===
if math.isnan(call_price):
    st.warning("⚠️ Could not fetch recent price for the SPY call option.")
    if time.time() - start_time > 60:
        call_price = st.number_input("🔧 Enter SPY Call Price manually ($):", min_value=0.01, value=0.0, step=0.01)
        if call_price > 0:
            spy_price = spy_price or st.number_input("Enter SPY spot price manually ($):", min_value=0.0)
            vix_value = vix_value or st.number_input("Enter VIX manually:", min_value=0.0)
            is_fallback = True
        else:
            st.stop()
    else:
        st.info("⏳ Waiting 60 seconds before allowing manual price input.")
        st.stop()
else:
    if is_fallback:
        st.info("ℹ️ Using previous day's close for SPY call price.")

# === Display Metrics ===
action, call_pct_change = check_trade(spy_price, vix_value, call_price)

st.metric(label="SPY Spot Price", value=f"${spy_price:.2f}")
st.metric(label="VIX (Volatility Index)", value=f"{vix_value:.2f}")
st.metric(label="Your SPY Call Price", value=f"${call_price:.2f}", delta=f"{call_pct_change:.1f}% vs entry")

# === Recommendation ===
st.header("🔗 Action Recommendation")
st.success(action) if "✅" in action else st.error(action)

st.caption("⏱️ Data refreshes manually. Click Rerun or refresh browser.")
st.markdown("---")
st.caption("Built by ChatGPT + You | Trading smarter, not harder. 🚀")
