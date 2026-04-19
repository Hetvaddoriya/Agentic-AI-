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

# ---------------- STYLE ----------------
st.markdown("""
<style>
.block-container {padding-top: 1rem;}
.stMetric {
    background: linear-gradient(135deg,#667eea,#764ba2);
    padding: 15px;
    border-radius: 12px;
    color: white;
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
    ["Dashboard", "➕ Add Event", "📅 Calendar", "🕒 Free Time", "🔔 Reminders", "🎯 Goals", "🤖 AI"])

# ---------------- STORAGE ----------------
if "events" not in st.session_state:
    st.session_state.events = []

if "goals" not in st.session_state:
    st.session_state.goals = []

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
    st.subheader("📊 Smart Dashboard")

    events = st.session_state.events

    total = len(events)
    upcoming = sum(1 for e in events if e["start"] > datetime.now())

    total_hours = sum(
        (e["end"] - e["start"]).total_seconds() / 3600
        for e in events
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Total Events", total)
    col2.metric("⏳ Upcoming", upcoming)
    col3.metric("🔥 Busy Hours", round(total_hours, 2))

    st.progress(min(total_hours / 24, 1.0))
    st.write(f"🕒 Day Utilization: {round(total_hours, 2)} hrs")

    # Chart
    if events:
        df = pd.DataFrame(events)
        df["date"] = df["start"].dt.date
        chart_data = df.groupby("date").size()

        st.markdown("### 📈 Events per Day")
        st.bar_chart(chart_data)

    else:
        st.info("No events")

    # Goals summary
    if st.session_state.goals:
        st.markdown("### 🎯 Goals Progress")
        for goal in st.session_state.goals:
            progress = total_hours
            percent = min(progress / goal["target"], 1.0)

            st.progress(percent)
            st.write(f"{goal['title']} → {round(percent*100)}%")

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
        if start >= end:
            st.error("End time must be greater than start time")
        else:
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

# ---------------- REMINDERS ----------------
elif menu == "🔔 Reminders":
    st.subheader("🔔 Alerts")

    now = datetime.now()

    for e in st.session_state.events:
        if e["reminder"] and now >= e["reminder"] and now < e["start"]:
            st.warning(f"Reminder: {e['title']}")
            st.audio("https://www.soundjay.com/buttons/beep-07.wav")

# ---------------- GOALS ----------------
elif menu == "🎯 Goals":
    st.subheader("🎯 Goal Tracker")

    goal_title = st.text_input("Goal Title")
    goal_target = st.number_input("Target Hours", min_value=1)

    if st.button("➕ Add Goal"):
        st.session_state.goals.append({
            "title": goal_title,
            "target": goal_target
        })
        st.success("Goal added")

    total_hours = sum(
        (e["end"] - e["start"]).total_seconds() / 3600
        for e in st.session_state.events
    )

    for goal in st.session_state.goals:
        st.markdown(f"### {goal['title']}")
        percent = min(total_hours / goal["target"], 1.0)

        st.progress(percent)
        st.write(f"{round(total_hours,1)} / {goal['target']} hrs")

        if percent >= 1:
            st.success("✅ Goal Achieved!")

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
