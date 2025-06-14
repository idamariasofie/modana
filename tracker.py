import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Hypotyreos Tracker", layout="centered")
st.title("🧠 Hypotyreos Tracker MVP")

# Inmatning
st.subheader("📅 Dagens inmatning")
date = datetime.now().strftime("%Y-%m-%d")
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
        "Notes": notes
    }])
    try:
        existing = pd.read_csv("tracker_data.csv")
        df = pd.concat([existing, new_entry], ignore_index=True)
    except FileNotFoundError:
        df = new_entry

    df.to_csv("tracker_data.csv", index=False)
    st.success("✅ Data sparad!")

# Visualisering
st.subheader("📊 Din historik")
try:
    df = pd.read_csv("tracker_data.csv")
    st.write(df.tail(7))
    st.line_chart(df.set_index("Date")[["Tiredness", "Mood", "Sleep"]])
except FileNotFoundError:
    st.info("Ingen data sparad ännu. Fyll i formuläret ovan.")
