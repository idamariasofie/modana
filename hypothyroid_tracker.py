
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
tab1, tab2 = st.tabs(["📜 Daily Log", "🦨 Cycle Tracking"])

with tab2:
    st.markdown("### 🧬 Cycle Tracking")
    today = datetime.now().date()
    period_file = "data/period_log.csv"

    # Always attempt to load existing period log
    period_log = pd.DataFrame()
    last_period = today

    if os.path.exists(period_file):
        try:
            period_log = pd.read_csv(period_file)
            period_log["date"] = pd.to_datetime(period_log["date"])
            if not period_log.empty:
                last_period = period_log["date"].max().date()
            else:
                st.info("🕒 No previous periods logged yet.")
        except Exception:
            st.warning("⚠️ Could not read period log file.")
    else:
        st.info("🕒 No period history found. Start tracking to get cycle insights.")

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

    def suggest_exercise(cycle_phase):
        suggestions = {
            "Menstruation": "Restorative yoga, light stretching, or rest.",
            "Follicular": "Cardio, strength training – good time for intense movement.",
            "Ovulation": "High-intensity workouts, group training.",
            "Luteal": "Moderate movement like walking, yoga, swimming.",
            "PMS or Irregular": "Gentle yoga, breathing exercises, journaling."
        }
        return suggestions.get(cycle_phase, "Move intuitively.")

    days_since = (today - last_period).days
    cycle_phase = get_cycle_phase(days_since)
    st.markdown(f"**Current cycle phase:** `{cycle_phase}`")
    st.markdown(f"💡 **Suggested exercise today:** _{suggest_exercise(cycle_phase)}_")

    # 📂 Download period log
    if os.path.exists(period_file):
        with open(period_file, "rb") as f:
            st.download_button("⬇️ Download your period log", f, file_name="period_log.csv")
    else:
        st.info("📬 No period data available yet.")

# tab1 (Daily Log) is re-added separately due to length
