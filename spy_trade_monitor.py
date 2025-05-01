# pip install streamlit yahooquery

import streamlit as st
from yahooquery import Ticker
import math

# === Settings ===
CALL_TICKER = 'SPY240117C00550000'
ENTRY_PRICE = 44.78  # Your cost basis

st.set_page_config(page_title="SPY Call Trade Monitor", page_icon="📈", layout="centered")
st.title("SPY Call Monitoring Dashboard 🚀")
st.write("Live monitoring for your SPY Jan 2026 $550c position")

# === Fetch SPY + VIX Spot Prices Only ===
def fetch_spy_and_vix():
    try:
        tickers = Ticker(["SPY", "^VIX"])
        spy_price = tickers["SPY"].price["SPY"]["regularMarketPrice"]
        vix_value = tickers["^VIX"].price["^VIX"]["regularMarketPrice"]
        return spy_price, vix_value, None
    except Exception as e:
        return None, None, str(e)

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
spy_price, vix_value, error = fetch_spy_and_vix()

if error:
    st.error(f"⚠️ Could not fetch SPY/VIX prices. You can enter them manually.")
    spy_price = st.number_input("Enter SPY Spot Price manually ($):", min_value=0.0)
    vix_value = st.number_input("Enter VIX manually:", min_value=0.0)

# === Manual Option Price Input ===
call_price = st.number_input("🔧 Enter your SPY Call Price ($):", min_value=0.01, value=0.01, step=0.01)

# === Proceed if call price is valid ===
if call_price > 0 and spy_price and vix_value:
    action, call_pct_change = check_trade(spy_price, vix_value, call_price)

    st.metric(label="SPY Spot Price", value=f"${spy_price:.2f}")
    st.metric(label="VIX (Volatility Index)", value=f"{vix_value:.2f}")
    st.metric(label="Your SPY Call Price", value=f"${call_price:.2f}", delta=f"{call_pct_change:.1f}% vs entry")

    st.header("🔗 Action Recommendation")
    st.success(action) if "✅" in action else st.error(action)
else:
    st.info("📥 Please enter all required values to proceed.")

st.caption("⏱️ Data refreshes manually. Click Rerun or refresh browser.")
st.markdown("---")
st.caption("Built by ChatGPT + You | Trading smarter, not harder. 🚀")
