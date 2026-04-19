import streamlit as st
from datetime import datetime, timedelta
from groq import Groq
from streamlit_calendar import calendar
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Timetable AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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

# ---------------- AI FUNCTION ----------------
def ai_response(user_input, events):
    try:
        schedule = "\n".join([f"{e['title']} ({e['start']} - {e['end']})" for e in events])
        prompt = f"{schedule}\n\n{user_input}"

        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        return chat.choices[0].message.content
    except Exception as e:
        return str(e)

# ---------------- AI REMINDER SUGGESTION ----------------
def suggest_reminder(start_time):
    # Suggest reminder 30 minutes before event
    return start_time - timedelta(minutes=30)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.subheader("📊 Dashboard")

    events = st.session_state.events
    total = len(events)

    st.metric("📅 Total Events", total)

# ---------------- ADD EVENT ----------------
elif menu == "➕ Add Event":
    st.subheader("➕ Add Event")

    title = st.text_input("Event Title")
    start = st.datetime_input("Start Time")
    end = st.datetime_input("End Time")

    auto_reminder = st.checkbox("🤖 Auto Suggest Reminder")

    if auto_reminder:
        reminder = suggest_reminder(start)
        st.info(f"Suggested Reminder: {reminder}")
    else:
        reminder = st.datetime_input("⏰ Set Reminder")

    if st.button("Add Event"):
        st.session_state.events.append({
            "title": title,
            "start": start,
            "end": end,
            "reminder": reminder
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
        for i in range(len(events)-1):
            if events[i]["end"] < events[i+1]["start"]:
                st.success(f"{events[i]['end']} → {events[i+1]['start']}")

# ---------------- REMINDERS ----------------
elif menu == "🔔 Reminders":
    st.subheader("🔔 Alerts")

    now = datetime.now()

    for e in st.session_state.events:
        if e["reminder"]:

            # Show upcoming reminders
            st.info(f"📌 {e['title']} → {e['reminder']}")

            # Trigger alert
            if now >= e["reminder"] and now < e["start"]:

                # 🔥 MOBILE-LIKE POPUP
                st.toast(f"⏰ {e['title']} starting soon!")

                # 🔊 SOUND
                st.audio("https://www.soundjay.com/buttons/beep-07.wav")

                # 🖥️ DESKTOP NOTIFICATION
                st.markdown(f"""
<script>
if (Notification.permission !== "granted") {{
    Notification.requestPermission();
}} else {{
    new Notification("Reminder", {{
        body: "{e['title']} is starting soon!",
        icon: "https://cdn-icons-png.flaticon.com/512/2921/2921222.png"
    }});
}}
</script>
""", unsafe_allow_html=True)

# ---------------- AI ----------------
elif menu == "🤖 AI":
    st.subheader("🤖 AI Assistant")

    user_input = st.text_input("Ask something")

    if st.button("Ask AI"):
        st.success(ai_response(user_input, st.session_state.events))

# ---------------- FOOTER ----------------
st.markdown("---")
