import streamlit as st
import pandas as pd
import os
import tempfile
import shutil
from datetime import datetime, date

# ----- Setup -----
os.makedirs("data", exist_ok=True)
log_file = "data/tracker_data.csv"
period_file = "data/period_log.csv"

# ----- Safe CSV handling -----
def safe_load_csv(file):
    try:
        if os.path.exists(file):
            df = pd.read_csv(file)
            return df
    except Exception:
        st.warning(f"⚠️ {file} was corrupted – a new file will be created.")
    return pd.DataFrame()

def safe_save_csv(df, file):
    """Safe saving with a temporary file to prevent corruption."""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='')
        df.to_csv(temp_file.name, index=False)
        shutil.move(temp_file.name, file)
    except Exception as e:
        st.error(f"❌ Could not save file {file}: {e}")

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

# ===================================================
# ---- TAB 1: DAILY LOG ----
# ===================================================
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

    log_id = f"{selected_date}_{entry_time}"

    # --- SAVE ENTRY ---
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
            if os.path.exists(log_file):
                # Create backup before changes
                backup_file = "data/tracker_data_backup.csv"
                pd.read_csv(log_file).to_csv(backup_file, index=False)

                existing = pd.read_csv(log_file)

                # Check column structure
                if not all(col in existing.columns for col in new_entry.columns if col != "LogID"):
                    st.error("⚠️ File structure seems to have changed – data was not saved. Please check your CSV file.")
                    st.stop()

                existing["LogID"] = existing["Date"].astype(str) + "_" + existing["Entry"]
                existing = existing[existing["LogID"] != log_id]
                df = pd.concat([existing, new_entry], ignore_index=True)
                df.drop(columns=["LogID"], inplace=True)
            else:
                df = new_entry.drop(columns=["LogID"])

            safe_save_csv(df, log_file)
            st.success("✅ Entry saved successfully (backup created).")

        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")


# ===================================================
# ---- TAB 2: CYCLE OVERVIEW ----
# ===================================================
with tab2:
    st.header("Cycle Overview")

    # Load cycle data
    cycle_df = safe_load_csv(period_file)

    # Input: Last menstruation date
    last_period = st.date_input("Last menstruation start date:", value=date.today())

    # Input: Average cycle length
    avg_cycle = st.number_input("Average cycle length (days):", min_value=20, max_value=40, value=28)

    if st.button("Save cycle data"):
        cycle_entry = pd.DataFrame([{
            "LastPeriod": last_period,
            "AvgCycle": avg_cycle
        }])
        safe_save_csv(cycle_entry, period_file)
        st.success("✅ Cycle information saved.")

    # Display current cycle phase
    if not cycle_df.empty:
        last_date = pd.to_datetime(cycle_df.iloc[-1]["LastPeriod"])
        cycle_length = int(cycle_df.iloc[-1]["AvgCycle"])
        today = pd.to_datetime(date.today())
        cycle_day = (today - last_date).days + 1
        phase = "Menstrual" if cycle_day <= 5 else "Follicular" if cycle_day <= 14 else "Ovulation" if cycle_day <= 17 else "Luteal"

        st.markdown(f"**Today is cycle day:** {cycle_day}")
        st.markdown(f"**Phase:** {phase}")

        # Training recommendation
        training_tip = {
            "Menstrual": "Focus on rest, light yoga or stretching.",
            "Follicular": "Energy rising – try strength training or cardio.",
            "Ovulation": "Peak energy – high-intensity workouts are great.",
            "Luteal": "Moderate exercise, listen to your body and avoid overtraining."
        }
        st.info(f"💡 Training tip: {training_tip[phase]}")

    # Combine all data for insights
    log_df = safe_load_csv(log_file)
    if not log_df.empty and not cycle_df.empty:
        st.subheader("Personalized Insights")
        avg_sleep = log_df["Sleep"].mean()
        sugar_days = log_df[log_df["Sugar"] == True].shape[0]
        tired_sugar = log_df[(log_df["Sugar"] == True) & (log_df["Tiredness"] >= 4)].shape[0]

        if avg_sleep < 7:
            st.write("😴 Try to aim for at least 7 hours of sleep – your average has been lower recently.")
        if tired_sugar > 0:
            st.write("🍭 You tend to feel more tired on days you eat sugar – consider reducing sugar intake.")

    # Download button
    if not log_df.empty:
        combined_data = log_df.copy()
        if not cycle_df.empty:
            combined_data["LastPeriod"] = cycle_df.iloc[-1]["LastPeriod"]
            combined_data["AvgCycle"] = cycle_df.iloc[-1]["AvgCycle"]

        csv = combined_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download all data (CSV)",
            data=csv,
            file_name=f"hypothyroid_tracker_data_{date.today()}.csv",
            mime="text/csv"
        )