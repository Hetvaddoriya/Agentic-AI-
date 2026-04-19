import streamlit as st
from datetime import datetime, timedelta
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Timetable AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ---------------- UI HEADER ----------------
st.markdown("""
# 📅 Smart Timetable Assistant AI
### 🚀 Smart Scheduling + AI Assistant
---
""")

# ---------------- LOCAL STORAGE ----------------
if "events" not in st.session_state:
    st.session_state.events = []

# ---------------- EMAIL FUNCTION ----------------
def send_email(subject, body, to_email):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = st.secrets["EMAIL_USER"]
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.error(f"Email Error: {e}")

# ---------------- AI FUNCTION ----------------
def ai_response(user_input, events):
    try:
        schedule_text = "\n".join(
            [f"{e['title']} ({e['start']} - {e['end']})" for e in events]
        ) if events else "No events"

        prompt = f"""
User schedule:
{schedule_text}

User request:
{user_input}

Give structured timetable or reminder advice.
"""

        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )

        return chat.choices[0].message.content

    except Exception as e:
        return f"❌ AI Error: {e}"

# ---------------- ADD EVENT ----------------
st.header("➕ Add Event")

title = st.text_input("Event Title")
start = st.datetime_input("Start Date & Time")
end = st.datetime_input("End Date & Time")
reminder = st.datetime_input("⏰ Reminder Time")
email = st.text_input("📧 Email for reminder")

if st.button("🚀 Create Event"):
    if start >= end:
        st.error("⚠️ End time must be greater than Start time")
    else:
        new_event = {
            "title": title,
            "start": start,
            "end": end,
            "reminder": reminder,
            "email": email
        }

        for event in st.session_state.events:
            if start == event["start"] and end == event["end"]:
                st.warning("⚠️ Duplicate event")
                st.stop()

        st.session_state.events.append(new_event)
        st.success("✅ Event added")

# ---------------- CALENDAR ----------------
st.header("📅 Calendar View")

from streamlit_calendar import calendar

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
st.header("🕒 Free Time Finder")

if st.button("Find Free Time"):
    events = sorted(st.session_state.events, key=lambda x: x["start"])

    if not events:
        st.success("🟢 Full day free")
    else:
        free_slots = []

        for i in range(len(events)-1):
            if events[i]["end"] < events[i+1]["start"]:
                free_slots.append((events[i]["end"], events[i+1]["start"]))

        if free_slots:
            best = max(free_slots, key=lambda x: x[1]-x[0])

            for s,e in free_slots:
                st.write(f"🟢 {s.strftime('%H:%M')} → {e.strftime('%H:%M')}")

            st.success(f"⭐ Best Slot: {best[0]} → {best[1]}")
        else:
            st.error("No free slots")

# ---------------- REMINDER SYSTEM ----------------
st.header("🔔 Reminders")

now = datetime.now()

for e in st.session_state.events:
    if e["reminder"] and now >= e["reminder"] and now < e["start"]:

        st.warning(f"⏰ Reminder: {e['title']} at {e['start']}")

        # 🔊 SOUND
        st.audio("https://www.soundjay.com/buttons/beep-07.wav")

        # 📧 EMAIL
        if e["email"]:
            send_email(
                f"Reminder: {e['title']}",
                f"Your event starts at {e['start']}",
                e["email"]
            )

# ---------------- AI ASSISTANT ----------------
st.header("🤖 Smart Assistant")

user_input = st.text_input("Ask something")

if st.button("Ask AI"):
    if user_input:
        st.success(ai_response(user_input, st.session_state.events))

if st.button("⚡ Auto Generate Study Plan"):
    if st.session_state.events:
        st.success(ai_response("Create full timetable", st.session_state.events))

# ---------------- FOOTER ----------------
st.markdown("---")
