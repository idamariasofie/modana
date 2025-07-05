import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

# ----- Ensure Data Directory Exists -----
os.makedirs("data", exist_ok=True)

# ----- Simple Password Protection -----
def check_password():
    def password_entered():
        if st.session_state["password"] == "mysecretpass":
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

# ----- App Layout Tabs -----
tab1, tab2 = st.tabs(["📝 Daily Log", "🩸 Cycle Tracking"])

with tab2:
    st.markdown("### 🧬 Cycle Tracking")
    today = datetime.now().date()

    period_file = "data/period_log.csv"
    manual_period = st.date_input("If you already know your last period start date, enter it here:", value=today)
    if st.button("Save this period start date"):
        new_period = pd.DataFrame([{"date": manual_period}])
        try:
            period_log = pd.read_csv(period_file)
            period_log["date"] = pd.to_datetime(period_log["date"])
            if manual_period not in period_log["date"].dt.date.values:
                period_log = pd.concat([period_log, new_period], ignore_index=True)
                period_log = period_log.drop_duplicates().sort_values("date")
                period_log.to_csv(period_file, index=False)
                st.success(f"Saved {manual_period} as period start date.")
            else:
                st.warning(f"{manual_period} is already logged.")
        except FileNotFoundError:
            new_period.to_csv(period_file, index=False)
            st.success(f"Saved {manual_period} as first period entry.")

    if st.button("📍 Log that period started today"):
        new_period = pd.DataFrame([{"date": today}])
        try:
            period_log = pd.read_csv(period_file)
            period_log["date"] = pd.to_datetime(period_log["date"])
            if today not in period_log["date"].dt.date.values:
                period_log = pd.concat([period_log, new_period], ignore_index=True)
                period_log = period_log.drop_duplicates().sort_values("date")
                period_log.to_csv(period_file, index=False)
                st.success("Logged today as a new period start!")
            else:
                st.warning("Today's date is already logged.")
        except FileNotFoundError:
            new_period.to_csv(period_file, index=False)
            st.success("Logged today as first period entry!")

    # Load last known period
    last_period = today
    try:
        period_log = pd.read_csv(period_file)
        period_log["date"] = pd.to_datetime(period_log["date"])
        if not period_log.empty:
            last_period = period_log["date"].max().date()
        else:
            st.info("🕒 No previous periods logged yet.")
    except Exception:
        st.info("🕒 No period history found. Start tracking to get cycle insights.")

    # Show period history with delete option
    if os.path.exists(period_file):
        st.markdown("### 🕰 Your period log history")
        period_log = pd.read_csv(period_file)
        period_log["date"] = pd.to_datetime(period_log["date"]).dt.date
        editable_log = period_log.sort_values("date", ascending=False).reset_index(drop=True)
        for i, row in editable_log.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.write(f"{row['date']}")
            if col2.button("Delete", key=f"delete_{i}"):
                editable_log = editable_log.drop(index=i).reset_index(drop=True)
                editable_log.to_csv(period_file, index=False)
                st.success("Deleted.")
                st.experimental_rerun()

    # Compute cycle phase
    def get_cycle_phase(days_since, cycle_length=28):
        if days_since <= 4:
            return "Menstruation"
        elif days_since <= (cycle_length // 2) - 2:
            return "Follicular"
        elif days_since <= cycle_length - 7:
            return "Ovulation"
        elif days_since <= cycle_length:
            return "Luteal"
        else:
            return "PMS or Irregular"

    days_since = (today - last_period).days
    cycle_phase = get_cycle_phase(days_since)
    st.markdown(f"**Current cycle phase:** `{cycle_phase}`")

with tab1:
    st.subheader("📅 Daily Entry")

    date = today.strftime("%Y-%m-%d")

    sleep_hours = st.slider("🛏️ Hours slept", 0, 12, 7)
    tiredness = st.slider("😴 Tiredness (1–5)", 1, 5, 3)
    mood = st.slider("🙂 Mood (1–5)", 1, 5, 3)
    energy = st.slider("⚡ Energy level (1–5)", 1, 5, 3)
    stress = st.slider("💼 Stress level (1–5)", 1, 5, 2)
    anxiety = st.slider("😟 Anxiety (1–5)", 1, 5, 2)

    took_meds = st.checkbox("💊 Took Levothyroxine today?")

    ate_gluten = st.checkbox("🍞 Ate gluten today?")
    ate_sugar = st.checkbox("🍬 Ate sugar today?")
    ate_dairy = st.checkbox("🥛 Ate dairy today?")
    ate_processed = st.checkbox("🍔 Ate processed food today?")

    water = st.slider("💧 Water intake (dl)", 0, 50, 20)
    coffee_cups = st.slider("☕ Coffee cups", 0, 6, 2)
    last_coffee = st.time_input("🕒 Time of last coffee")

    exercised = st.checkbox("🏃‍♀️ Did you exercise today?")
    if exercised:
        exercise_type = st.selectbox("Type of exercise", ["Walk", "Strength", "Yoga", "Cardio", "Other"])
        exercise_duration = st.slider("Duration (minutes)", 0, 180, 30)
        exercise_intensity = st.radio("Intensity", ["Low", "Moderate", "High"])
    else:
        exercise_type = ""
        exercise_duration = 0
        exercise_intensity = ""

    weather = st.selectbox("🌦️ Weather impact", ["Sunny", "Cloudy", "Rainy", "Cold", "Hot"])
    temperature_feel = st.radio("🌡️ Temperature perception", ["Cold", "Normal", "Warm"])
    sleep_env = st.multiselect("🛌 Sleep environment", ["Quiet", "Noisy", "Warm", "Cool"])

    notes = st.text_area("📝 Additional notes (optional)")

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

        tracker_file = "data/tracker_data.csv"
        try:
            existing = pd.read_csv(tracker_file)
            if date in existing["Date"].values:
                st.warning("An entry for today already exists. Overwriting...")
                existing = existing[existing["Date"] != date]
            df = pd.concat([existing, new_entry], ignore_index=True)
        except FileNotFoundError:
            df = new_entry

        df.to_csv(tracker_file, index=False)
        st.success("✅ Entry saved!")
    
    # 💾 Ladda ner menscykellogg
    if os.path.exists(period_file):
        with open(period_file, "rb") as f:
            st.download_button("⬇️ Download your period log", f, file_name="period_log.csv")
    else:
        st.info("📭 No period data available yet.")