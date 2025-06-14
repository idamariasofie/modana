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

# ----- Menstrual Cycle Input -----
st.sidebar.title("🩸 Cycle Settings")
period_start = st.sidebar.date_input("When did your last period start?")

def get_cycle_phase(current_date, period_start):
    cycle_length = 28
    days_since = (current_date - period_start).days % cycle_length
    if days_since <= 4:
        return "Menstruation"
    elif days_since <= 13:
        return "Follicular"
    elif days_since <= 21:
        return "Luteal"
    else:
        return "PMS"

today = datetime.now().date()
cycle_phase = get_cycle_phase(today, period_start)
st.sidebar.markdown(f"**Current phase:** `{cycle_phase}`")

# ----- Daily Input Form -----
st.subheader("📅 Daily Entry")
date = today.strftime("%Y-%m-%d")

# Sleep & Mental State
sleep_hours = st.slider("🛏️ Hours slept", 0, 12, 7)
tiredness = st.slider("😴 Tiredness (1–5)", 1, 5, 3)
mood = st.slider("🙂 Mood (1–5)", 1, 5, 3)
energy = st.slider("⚡ Energy level (1–5)", 1, 5, 3)
stress = st.slider("💼 Stress level (1–5)", 1, 5, 2)
anxiety = st.slider("😟 Anxiety (1–5)", 1, 5, 2)

# Medication
took_meds = st.checkbox("💊 Took Levothyroxine today?")

# Diet
ate_gluten = st.checkbox("🍞 Ate gluten today?")
ate_sugar = st.checkbox("🍬 Ate sugar today?")
ate_dairy = st.checkbox("🥛 Ate dairy today?")
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
    new_entry = pd.DataFrame([{
        "Date": date,
        "CyclePhase": cycle_phase,
        "Sleep": sleep_hours,
        "Tiredness": tiredness,
        "Mood": mood,
        "Energy": energy,
        "Stress": stress,
        "Anxiety": anxiety,
        "TookMedication": took_meds,
        "Gluten": ate_gluten,
        "Sugar": ate_sugar,
        "Dairy": ate_dairy,
        "ProcessedFood": ate_processed,
        "WaterIntake": water,
        "CoffeeCups": coffee_cups,
        "LastCoffee": str(last_coffee),
        "Exercised": exercised,
        "ExerciseType": exercise_type,
        "ExerciseDuration": exercise_duration,
        "ExerciseIntensity": exercise_intensity,
        "Weather": weather,
        "TempFeel": temperature_feel,
        "SleepEnvironment": ", ".join(sleep_env),
        "Notes": notes
    }])

    try:
        existing = pd.read_csv("tracker_data.csv")
        df = pd.concat([existing, new_entry], ignore_index=True)
    except FileNotFoundError:
        df = new_entry

    df.to_csv("tracker_data.csv", index=False)
    st.success("✅ Entry saved!")

# ----- Data Preview -----
st.subheader("📊 Your recent data")
try:
    df = pd.read_csv("tracker_data.csv")
    st.write(df.tail(7))
    st.line_chart(df.set_index("Date")[["Tiredness", "Mood", "Sleep", "Energy"]])
except FileNotFoundError:
    st.info("No data saved yet. Fill out today's entry first.")

# ----- AI Insight (Prediction) -----
st.subheader("🔍 AI Insight – Predict your tiredness")

try:
    df = pd.read_csv("tracker_data.csv")
    df["Gluten"] = df["Gluten"].astype(int)
    df["Sugar"] = df["Sugar"].astype(int)
    df["ProcessedFood"] = df["ProcessedFood"].astype(int)
    df["Dairy"] = df["Dairy"].astype(int)
    df["Exercised"] = df["Exercised"].astype(int)

    X = df[["Sleep", "Mood", "Energy", "Stress", "Gluten", "Sugar", "ProcessedFood", "Exercised"]]
    y = df["Tiredness"]

    model = RandomForestRegressor()
    model.fit(X, y)

    input_data = pd.DataFrame([[
        sleep_hours,
        mood,
        energy,
        stress,
        int(ate_gluten),
        int(ate_sugar),
        int(ate_processed),
        int(exercised)
    ]], columns=X.columns)

    prediction = model.predict(input_data)[0]
    st.markdown(f"🧠 AI predicts your tiredness today to be: **{prediction:.1f}**")

except Exception:
    st.warning("⚠️ AI model cannot run yet – please log more days first.")

# ----- Weekly Summary -----
st.subheader("📆 Weekly Summary")

if os.path.exists("tracker_data.csv"):
    try:
        df = pd.read_csv("tracker_data.csv")
        df["Date"] = pd.to_datetime(df["Date"])
        last_7_days = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=7)]

        if last_7_days.empty:
            st.info("You need at least one week's worth of data to generate a summary.")
        else:
            st.markdown("### Averages (last 7 days)")
            metrics = ["Tiredness", "Mood", "Energy", "Stress", "Anxiety", "Sleep"]
            for metric in metrics:
                if metric in last_7_days.columns:
                    avg = last_7_days[metric].mean()
                    st.write(f"**{metric}**: {avg:.2f}")

            st.markdown("### Most common notes")
            if "Notes" in last_7_days.columns:
                notes = last_7_days["Notes"].dropna().value_counts().head(3)
                for i, (text, count) in enumerate(notes.items(), 1):
                    st.write(f"{i}. {text} ({count}x)")

    except Exception as e:
        st.error(f"Error generating weekly summary: {e}")
else:
    st.info("No data file found yet. Save your first entry to begin tracking.")

# ----- Cycle Phase Insights -----
st.subheader("📈 Insights by Cycle Phase")

if 'df' in locals() or 'df' in globals():
    try:
        if "CyclePhase" in df.columns:
            phase_avg = df.groupby("CyclePhase")[["Tiredness", "Mood", "Energy", "Stress"]].mean()
            st.dataframe(phase_avg.style.format("{:.2f}"))
            st.markdown("This table shows your average levels across each menstrual phase.")
        else:
            st.info("Cycle phase data is missing in your logs.")
    except Exception as e:
        st.error(f"Error analyzing by cycle phase: {e}")
else:
    st.info("No data loaded yet.")
