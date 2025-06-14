
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

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

    manual_period = st.date_input("If you already know your last period start date, enter it here:", value=today)
    if st.button("Save this period start date"):
        new_period = pd.DataFrame([{"date": manual_period}])
        try:
            period_log = pd.read_csv("period_log.csv")
            period_log = pd.concat([period_log, new_period], ignore_index=True)
            period_log["date"] = pd.to_datetime(period_log["date"])
            period_log = period_log.drop_duplicates().sort_values("date")
        except FileNotFoundError:
            period_log = new_period
        period_log.to_csv("period_log.csv", index=False)
        st.success(f"Saved {manual_period} as period start date.")

    if st.button("📍 Log that period started today"):
        new_period = pd.DataFrame([{"date": today}])
        try:
            period_log = pd.read_csv("period_log.csv")
            period_log = pd.concat([period_log, new_period], ignore_index=True)
            period_log["date"] = pd.to_datetime(period_log["date"])
            period_log = period_log.drop_duplicates().sort_values("date")
        except FileNotFoundError:
            period_log = new_period
        period_log.to_csv("period_log.csv", index=False)
        st.success("Logged today as a new period start!")

    # Load last known period
    last_period = today
    try:
        period_log = pd.read_csv("period_log.csv")
        period_log["date"] = pd.to_datetime(period_log["date"])
        if not period_log.empty:
            last_period = period_log["date"].max().date()
        else:
            st.info("🕒 No previous periods logged yet.")
    except Exception:
        st.info("🕒 No period history found. Start tracking to get cycle insights.")

    # Show period history with delete option
    if os.path.exists("period_log.csv"):
        st.markdown("### 🕰 Your period log history")
        period_log = pd.read_csv("period_log.csv")
        period_log["date"] = pd.to_datetime(period_log["date"]).dt.date
        editable_log = period_log.sort_values("date", ascending=False).reset_index(drop=True)
        for i, row in editable_log.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.write(f"{row['date']}")
            if col2.button("Delete", key=f"delete_{i}"):
                editable_log = editable_log.drop(index=i).reset_index(drop=True)
                editable_log.to_csv("period_log.csv", index=False)
                st.success("Deleted. Please reload the app manually to see changes.")

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

with tab1:
    st.subheader("📅 Daily Entry")