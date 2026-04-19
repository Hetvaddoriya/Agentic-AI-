import streamlit as st
from datetime import datetime, time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Timetable AI", layout="wide")

# ---------------- UI HEADER ----------------
st.markdown("""
# 📅 Smart Timetable Assistant AI
### 🚀 Smart Scheduling + AI Assistant
---
""")

# ---------------- LOCAL STORAGE ----------------
if "events" not in st.session_state:
    st.session_state.events = []

# ---------------- SMART AI ----------------
def smart_response(user_input, events):
    user_input = user_input.lower()

    if not events:
        return "📅 You have a free schedule!"

    if "free" in user_input:
        return "🕒 Click 'Find Free Time' to see available slots."

    if "study" in user_input:
        return "📚 Best time to study is during long uninterrupted free slots."

    return f"💡 Try scheduling '{user_input}' in your free time."

# ---------------- ADD EVENT ----------------
st.header("➕ Add Event")

title = st.text_input("Event Title")
start = st.time_input("Start Time")
end = st.time_input("End Time")

if st.button("🚀 Create Event"):
    if start >= end:
        st.error("⚠️ End time must be greater than Start time")

    else:
        new_event = {
            "title": title,
            "start": start,
            "end": end
        }

        conflict = False
        for event in st.session_state.events:
            if (start < event["end"] and end > event["start"]):
                conflict = True
                break

        if conflict:
            st.error("⚠️ Conflict detected! Event not added ❌")
        else:
            st.session_state.events.append(new_event)
            st.success("✅ Event added successfully")

# ---------------- VIEW EVENTS ----------------
st.header("📅 Schedule")

if st.session_state.events:
    for e in st.session_state.events:
        st.write(f"📌 {e['title']} | {e['start']} → {e['end']}")
else:
    st.write("No events")

# ---------------- FREE TIME ----------------
st.header("🕒 Free Time Finder")

if st.button("Find Free Time"):
    events = sorted(st.session_state.events, key=lambda x: x["start"])

    if not events:
        st.write("🟢 Full day is free!")
    
    else:
        found = False

        # Before first event
        if events[0]["start"] > time(0, 0):
            st.write(f"🟢 Free: 00:00 → {events[0]['start']}")
            found = True

        # Between events
        for i in range(len(events) - 1):
            if events[i]["end"] < events[i+1]["start"]:
                st.write(f"🟢 Free: {events[i]['end']} → {events[i+1]['start']}")
                found = True

        # After last event
        if events[-1]["end"] < time(23, 59):
            st.write(f"🟢 Free: {events[-1]['end']} → 23:59")
            found = True

        if not found:
            st.write("⚠️ No free time available")

# ---------------- AI ASSISTANT ----------------
st.header("🤖 Smart Assistant")

user_input = st.text_input("Ask something (e.g., when am I free?)")

if st.button("Ask AI"):
    if user_input:
        response = smart_response(user_input, st.session_state.events)
        st.success(response)

# ---------------- FOOTER ----------------
st.markdown("---")
