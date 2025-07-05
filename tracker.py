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
                period_log = pd.concat([period_log, new_period], ignore_index=Tru