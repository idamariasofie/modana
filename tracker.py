import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

# ----- Simple Password Protection -----
def check_password():
    def password_entered():
        if st.session_state["password"] == "mysecretpass":  # 🔑 Change this to your own password!
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
            st.error("Incorrect password")

    if "authenticated" not in st.session_state:
        st.text_input("🔐 Enter password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["authenticated"]:
        st.text_input("🔐 Enter password:", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if not check_password():
    st.stop()

# ----- App Config -----
st.set_page_config(page_title="Hypothyroid Tracker", layout="centered")
st.title("🧠 Hypothyroid Tracker – Detailed MVP")

# ----- Cycle Logging -----
st.markdown("### 🧸 Cycle Tracking")
today = datetime.now().date()

if st.button("📍 Log that period started today"):
    new_period = pd.DataFrame([{"date": today}])
    try:
        period_log = pd.read_csv("period_log.csv")
        period_log = pd.concat([period_log, new_period], ignore_index=True)
    except FileNotFoundError:
        period_log = new_period

    period_log.to_csv("period_log.csv", index=False)
    st.success("Logged today as a new period start!")

# Load last known period
try:
    period_log = pd.read_csv("period_log.csv")
    period_log["date"] = pd.to_datetime(period_log["date"])
    last_period = period_log["date"].max().date()
except:
    last_period = today
    st.info("🔔 When your period starts, tap the button above to begin cycle tracking.")

# Compute cycle phase
def get_cycle_phase(days_since):
    if days_since <= 4:
        return "Menstruation"
    elif days_since <= 13:
        return "Follicular"
    elif days_since <= 21:
        return "Luteal"
    else:
        return "PMS"

days_since = (today - last_period).days
cycle_phase = get_cycle_phase(days_since)
st.markdown(f"**Current cycle phase:** `{cycle_phase}`")

# ----- Daily Input Form -----
st.subheader("🗕️ Daily Entry")
date = today.strftime("%Y-%m-%d")

# Sleep & Mental State
sleep_hours = st.slider("🛏️ Hours slept", 0, 12, 7)
tiredness = st.slider("😬 Tiredness (1–5)", 1, 5, 3)
mood = st.slider("🙂 Mood (1–5)", 1, 5, 3)
energy = st.slider("⚡ Energy level (1–5)", 1, 5, 3)
stress = st.slider("💼 Stress level (1–5)", 1, 5, 2)
anxiety = st.slider("😟 Anxiety (1–5)", 1, 5, 2)

# Medication
took_meds = st.checkbox("💊 Took Levothyroxine today?")

# Diet
ate_gluten = st.checkbox("🍞 Ate gluten today?")
ate_sugar = st.checkbox("🍬 Ate sugar today?")
ate_dairy = st.checkbox("🧋 Ate dairy today?")
ate_processed = st.checkbox("🍔 Ate processed food today?")

# Fluids & Caffeine
water = st.slider("💧 Water intake (dl)", 0, 50, 20)
coffee_cups = st.slider("☕ Coffee cups", 0, 6, 2)
last_coffee = st.time_input("🕒 Time of last coffee")

# Exercise
exercised = st.checkbox("🏃‍♀️ Did you exercise today?")
if exercised:
    exercise_type = st.selectbox("Type of exercise", ["Walk", "Strength", "Yoga", "Cardio", "Other"])
    exercise_duration = st.slider("Duration (minutes)", 0, 180, 30)
    exercise_intensity = st.radio("Intensity", ["Low", "Moderate", "High"])
else:
    exercise_type = ""
    exercise_duration = 0
    exercise_intensity = ""

# External Factors
weather = st.selectbox("🌦️ Weather impact", ["Sunny", "Cloudy", "Rainy", "Cold", "Hot"])
temperature_feel = st.radio("🌡️ Temperature perception", ["Cold", "Normal", "Warm"])
sleep_env = st.multiselect("🛌 Sleep environment", ["Quiet", "Noisy", "Warm", "Cool"])

# Notes
notes = st.text_area("📝 Additional notes (optional)")

# ----- Save Data -----
if st.button("💾 Save entry"):
    new_entry = pd.DataFrame([{...}])  # (Keeping placeholder to shorten code here)

# (Rest of the code remains unchanged for saving, visualizing, AI insights, and summaries)