import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from sklearn.ensemble import RandomForestRegressor

# ----- Setup -----
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
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["authenticated"]:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if not check_password():
    st.stop()

# ----- App Config -----
st.set_page_config(page_title="Hypothyroid Tracker", layout="centered")
st.title("Hypothyroid Tracker")

# ----- Tabs -----
tab1, tab2 = st.tabs(["Daily Check-In", "Cycle Overview"])

# ---- Tab 1: Daily Log ----
with tab1:
    st.header("How are you today?")
    selected_date = st.date_input("Log for date:", value=date.today())
    entry_time = st.radio("Entry Type", ["Morning", "Evening"], horizontal=True)

    sleep_hours = st.slider("Hours slept", 0, 12, 7)
    tiredness = st.radio("Tiredness (1–5)", options=[1, 2, 3, 4, 5], horizontal=True)
    mood = st.radio("Mood (1–5)", options=[1, 2, 3, 4, 5], horizontal=True)
    self_worth = st.radio("Self-worth (1–5)", options=[1, 2, 3, 4, 5], horizontal=True)
    energy = st.radio("Energy (1–5)", options=[1, 2, 3, 4, 5], horizontal=True)
    stress = st.radio("Stress (1–5)", options=[1, 2, 3, 4, 5], horizontal=True)
    anxiety = st.radio("Anxiety (1–5)", options=[1, 2, 3, 4, 5], horizontal=True)

    took_meds = st.checkbox("Took medication today?")
    swollen = st.checkbox("Feeling swollen?")
    pain_level = st.slider("Overall pain (0–10)", 0, 10, 0)
    headache = st.checkbox("Headache")
    stomach = st.checkbox("Stomach pain")
    joints = st.checkbox("Joint or muscle pain")

    ate_gluten = st.checkbox("Ate gluten")
    ate_sugar = st.checkbox("Ate sugar")
    ate_dairy = st.checkbox("Ate dairy")
    processed = st.checkbox("Ate processed food")

    water = st.slider("Water intake (dl)", 0, 50, 20)
    coffee = st.slider("Coffee cups", 0, 6, 2)
    last_coffee = st.time_input("Last coffee time")

    exercised = st.checkbox("Exercised today?")
    if exercised:
        ex_type = st.selectbox("Exercise type", ["Walk", "Strength", "Yoga", "Cardio", "Other"])
        ex_duration = st.slider("Duration (min)", 0, 180, 30)
        ex_intensity = st.radio("Intensity", ["Low", "Moderate", "High"], horizontal=True)
    else:
        ex_type = ""
        ex_duration = 0
        ex_intensity = ""

    weather = st.selectbox("Weather", ["Sunny", "Cloudy", "Rainy", "Cold", "Hot"])
    temp_feel = st.radio("Temperature feel", ["Cold", "Normal", "Warm"], horizontal=True)
    sleep_env = st.multiselect("Sleep environment", ["Quiet", "Noisy", "Warm", "Cool"])
    notes = st.text_area("Anything else to note?")

    log_file = "data/tracker_data.csv"
    log_id = f"{selected_date}_{entry_time}"

    if st.button("Save entry"):
        new_entry = pd.DataFrame([{
            "Date": selected_date,
            "Entry": entry_time,
            "Sleep": sleep_hours,
            "Tiredness": tiredness,
            "Mood": mood,
            "SelfWorth": self_worth,
            "Energy": energy,
            "Stress": stress,
            "Anxiety": anxiety,
            "Medication": took_meds,
            "Swollen": swollen,
            "Pain": pain_level,
            "Headache": headache,
            "StomachPain": stomach,
            "JointPain": joints,
            "Gluten": ate_gluten,
            "Sugar": ate_sugar,
            "Dairy": ate_dairy,
            "Processed": processed,
            "Water": water,
            "Coffee": coffee,
            "LastCoffee": str(last_coffee),
            "Exercised": exercised,
            "ExerciseType": ex_type,
            "ExerciseDuration": ex_duration,
            "ExerciseIntensity": ex_intensity,
            "Weather": weather,
            "TempFeel": temp_feel,
            "SleepEnv": ", ".join(sleep_env),
            "Notes": notes
        }])
        new_entry["LogID"] = log_id

        try:
            existing = pd.read_csv(log_file)
            existing["LogID"] = existing["Date"].astype(str) + "_" + existing["Entry"]
            existing = existing[existing["LogID"] != log_id]
            df = pd.concat([existing, new_entry], ignore_index=True)
            df.drop(columns=["LogID"], inplace=True)
        except FileNotFoundError:
            df = new_entry.drop(columns=["LogID"])

        df.to_csv(log_file, index=False)
        st.success("Entry saved successfully.")

    if os.path.exists(log_file):
        with open(log_file, "rb") as f:
            st.download_button("Download my data", f, file_name="tracker_data.csv")

# -------------------- CYCLE TRACKING --------------------
with tab2:
    st.header("Cycle Phase Insight")

    today = date.today()
    period_file = "data/period_log.csv"
    period_log = pd.DataFrame()
    last_period = today

    if os.path.exists(period_file):
        try:
            period_log = pd.read_csv(period_file)
            period_log["date"] = pd.to_datetime(period_log["date"], errors="coerce")
            period_log = period_log.dropna(subset=["date"])
            if not period_log.empty:
                last_period = period_log["date"].max().date()
        except Exception:
            st.warning("Could not read period log file.")
    else:
        st.info("No period history found yet.")

    manual_period = st.date_input("Log a new period start date", value=today)
    if st.button("Save period start date"):
        new_period = pd.DataFrame([{"date": pd.Timestamp(manual_period)}])
        try:
            period_log = pd.read_csv(period_file)
            period_log["date"] = pd.to_datetime(period_log["date"], errors="coerce")
            period_log = period_log.dropna(subset=["date"])
            if pd.Timestamp(manual_period) not in period_log["date"].values:
                period_log = pd.concat([period_log, new_period], ignore_index=True)
                period_log = period_log.drop_duplicates().sort_values("date")
                period_log.to_csv(period_file, index=False)
                st.success(f"{manual_period} saved.")
            else:
                st.warning("Date already exists.")
        except FileNotFoundError:
            new_period.to_csv(period_file, index=False)
            st.success("First period entry saved.")

    def get_user_average_cycle_length():
        try:
            df = pd.read_csv(period_file)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            if len(df) >= 2:
                diffs = df["date"].diff().dropna().dt.days
                return int(diffs.mean())
        except Exception:
            pass
        return 28

    def get_cycle_phase(days_since, cycle_length):
        if days_since <= 4:
            return "Menstruation"
        elif 5 <= days_since <= 12:
            return "Follicular"
        elif 13 <= days_since <= 16:
            return "Ovulation"
        elif 17 <= days_since <= cycle_length:
            return "Luteal"
        else:
            return "PMS or Irregular"

    def suggest_exercise(cycle_phase):
        suggestions = {
            "Menstruation": "Gentle yoga, rest, short walks.",
            "Follicular": "Strength training, cardio.",
            "Ovulation": "High-intensity workouts.",
            "Luteal": "Moderate movement: swimming, pilates.",
            "PMS or Irregular": "Mindful movement and rest."
        }
        return suggestions.get(cycle_phase, "Move in a way that feels right.")

    days_since = (today - last_period).days
    user_cycle_length = get_user_average_cycle_length()
    cycle_phase = get_cycle_phase(days_since, user_cycle_length)

    st.subheader(f"Today’s Cycle Phase: {cycle_phase}")
    st.caption(f"Based on your average cycle of ~{user_cycle_length} days")
    st.markdown(f"**Suggested movement:** _{suggest_exercise(cycle_phase)}_")