import streamlit as st
from datetime import datetime
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from streamlit_calendar import calendar
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Timetable AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ---------------- ANIMATED UI STYLE ----------------
st.markdown("""
<style>
.block-container {padding-top: 1rem;}

.card {
    padding: 20px;
    border-radius: 15px;
    background: #ffffff;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.03);
    box-shadow: 0px 6px 20px rgba(0,0,0,0.2);
}

.stButton>button {
    border-radius: 12px;
    background: linear-gradient(90deg,#667eea,#764ba2);
    color: white;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div style='padding:20px;border-radius:15px;
background:linear-gradient(90deg,#667eea,#764ba2);color:white'>
<h2>📅 Smart Timetable Dashboard</h2>
<p>Plan • Track • Optimize your time</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("📌 Menu",
    ["Dashboard", "➕ Add Event", "📅 Calendar", "🕒 Free Time", "🔔 Reminders", "🤖 AI"])

# ---------------- STORAGE ----------------
if "events" not in st.session_state:
    st.session_state.events = []

# ---------------- AI ----------------
def ai_response(user_input, events):
    try:
        schedule_text = "\n".join(
            [f"{e['title']} ({e['start']} - {e['end']})" for e in events]
        ) if events else "No events"

        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": f"{schedule_text}\n\n{user_input}"}],
            model="llama-3.1-8b-instant"
        )
        return chat.choices[0].message.content
    except Exception as e:
        return str(e)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.subheader("📊 Overview")

    total_events = len(st.session_state.events)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<div class='card'><h3>Total Events</h3><h1>{total_events}</h1></div>", unsafe_allow_html=True)

    with col2:
        upcoming = sum(1 for e in st.session_state.events if e["start"] > datetime.now())
        st.markdown(f"<div class='card'><h3>Upcoming Events</h3><h1>{upcoming}</h1></div>", unsafe_allow_html=True)

    # 📊 Chart
    if st.session_state.events:
        df = pd.DataFrame(st.session_state.events)
        df["date"] = df["start"].dt.date
        chart_data = df.groupby("date").size()

        st.subheader("📈 Events per Day")
        st.line_chart(chart_data)

# ---------------- ADD EVENT ----------------
elif menu == "➕ Add Event":
    st.subheader("➕ Create Event")

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("Title")
        start = st.datetime_input("Start")

    with col2:
        end = st.datetime_input("End")
        reminder = st.datetime_input("Reminder")

    email = st.text_input("Email")

    if st.button("🚀 Add Event"):
        st.session_state.events.append({
            "title": title,
            "start": start,
            "end": end,
            "reminder": reminder,
            "email": email
        })
        st.success("Event added")

# ---------------- CALENDAR ----------------
elif menu == "📅 Calendar":
    st.subheader("📅 Calendar")

    calendar_events = [
        {
            "title": e["title"],
            "start": e["start"].isoformat(),
            "end": e["end"].isoformat()
        }
        for e in st.session_state.events
    ]

    calendar(events=calendar_events)

# ---------------- FREE TIME ----------------
elif menu == "🕒 Free Time":
    st.subheader("🕒 Free Time")

    if st.button("Find Free Time"):
        events = sorted(st.session_state.events, key=lambda x: x["start"])
        free_slots = []

        for i in range(len(events)-1):
            if events[i]["end"] < events[i+1]["start"]:
                free_slots.append((events[i]["end"], events[i+1]["start"]))

        if free_slots:
            best = max(free_slots, key=lambda x: x[1]-x[0])

            for s,e in free_slots:
                st.info(f"{s.strftime('%H:%M')} → {e.strftime('%H:%M')}")

            st.success(f"⭐ Best Slot: {best[0]} → {best[1]}")
        else:
            st.warning("No free time")

# ---------------- REMINDER ----------------
elif menu == "🔔 Reminders":
    st.subheader("🔔 Alerts")

    now = datetime.now()

    for e in st.session_state.events:
        if now >= e["reminder"] and now < e["start"]:
            st.warning(f"Reminder: {e['title']}")
            st.audio("https://www.soundjay.com/buttons/beep-07.wav")

# ---------------- AI ----------------
elif menu == "🤖 AI":
    st.subheader("🤖 Smart Assistant")

    user_input = st.text_input("Ask something")

    if st.button("Ask AI"):
        st.success(ai_response(user_input, st.session_state.events))

    if st.button("⚡ Auto Plan"):
        st.success(ai_response("Create full timetable", st.session_state.events))

# ---------------- FOOTER ----------------
st.markdown("---")
