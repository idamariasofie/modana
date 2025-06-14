import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

# ----- Konfiguration -----
st.set_page_config(page_title="Hypotyreos Tracker", layout="centered")
st.title("🧠 Hypotyreos Tracker MVP")

# ----- Menscykelinställningar i sidofältet -----
st.sidebar.title("🩸 Cykelinställningar")
period_start = st.sidebar.date_input("När började din senaste mens?")

def get_cycle_phase(current_date, period_start):
    cycle_length = 28
    days_since = (current_date - period_start).days % cycle_length
    if days_since <= 4:
        return "Mens"
    elif days_since <= 13:
        return "Folikelfas"
    elif days_since <= 21:
        return "Lutealfas"
    else:
        return "PMS"

today = datetime.now().date()
cycle_phase = get_cycle_phase(today, period_start)
st.sidebar.markdown(f"**Du är i:** `{cycle_phase}`")

# ----- Daglig inmatning -----
st.subheader("📅 Dagens inmatning")
date = today.strftime("%Y-%m-%d")
sleep_hours = st.slider("🛏️ Hur många timmar sov du?", 0, 12, 7)
tiredness = st.slider("😴 Trötthet (1–5)", 1, 5, 3)
mood = st.slider("🙂 Humör (1–5)", 1, 5, 3)
took_meds = st.checkbox("💊 Tog du Levaxin idag?")
ate_gluten = st.checkbox("🍞 Åt du gluten idag?")
exercise = st.checkbox("🏃‍♀️ Tränade du idag?")
notes = st.text_area("📝 Anteckningar (valfritt)")

if st.button("💾 Spara dagens data"):
    new_entry = pd.DataFrame([{
        "Date": date,
        "Sleep": sleep_hours,
        "Tiredness": tiredness,
        "Mood": mood,
        "Med": took_meds,
        "Gluten": ate_gluten,
        "Exercise": exercise,
        "CyclePhase": cycle_phase,
        "Notes": notes
    }])
    try:
        existing = pd.read_csv("tracker_data.csv")
        df = pd.concat([existing, new_entry], ignore_index=True)
    except FileNotFoundError:
        df = new_entry

    df.to_csv("tracker_data.csv", index=False)
    st.success("✅ Data sparad!")

# ----- Visualisering -----
st.subheader("📊 Din historik")
try:
    df = pd.read_csv("tracker_data.csv")
    st.write(df.tail(7))
    st.line_chart(df.set_index("Date")[["Tiredness", "Mood", "Sleep"]])
except FileNotFoundError:
    st.info("Ingen data sparad ännu. Fyll i formuläret ovan.")

# ----- Enkel AI-modell: Förutsäg trötthet -----
st.subheader("🔍 AI-insikt – Förutsäg trötthet")

try:
    df = pd.read_csv("tracker_data.csv")

    # Säkerställ rätt datatyper
    df["Gluten"] = df["Gluten"].astype(int)
    df["Exercise"] = df["Exercise"].astype(int)

    X = df[["Sleep", "Mood", "Gluten", "Exercise"]]
    y = df["Tiredness"]

    model = RandomForestRegressor()
    model.fit(X, y)

    # Skapa indata från dagens registrering
    input_data = pd.DataFrame([[
        sleep_hours,
        mood,
        int(ate_gluten),
        int(exercise)
    ]], columns=["Sleep", "Mood", "Gluten", "Exercise"])

    predicted_tiredness = model.predict(input_data)[0]
    st.markdown(f"🧠 AI-modellen förutspår att din trötthet idag är: **{predicted_tiredness:.1f}**")

except Exception as e:
    st.warning("⚠️ För lite data för att AI-modellen ska kunna göra en förutsägelse ännu.")
