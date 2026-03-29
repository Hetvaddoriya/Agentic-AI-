import streamlit as st
from calendar_utils import create_event, get_events
from scheduler import is_conflict
from agent import get_response
from datetime import datetime

st.title("📅 Smart Timetable Assistant AI")

# ---- ADD EVENT ----
st.header("Add Event")

title = st.text_input("Event Title")
start = st.datetime_input("Start Time")
end = st.datetime_input("End Time")

if st.button("Add Event"):
    events = get_events()

    conflict = is_conflict(
        events,
        start.isoformat(),
        end.isoformat()
    )

    if conflict:
        st.error("⚠️ Conflict detected! Choose another time.")
    else:
        link = create_event(title, start.isoformat(), end.isoformat())
        st.success(f"✅ Event Created: {link}")

# ---- VIEW EVENTS ----
st.header("Upcoming Events")

events = get_events()
for event in events:
    st.write(f"📌 {event['summary']} - {event['start']['dateTime']}")

# ---- AI ASSISTANT ----
st.header("AI Assistant")

user_input = st.text_input("Ask anything (e.g., find free time)")

if st.button("Ask AI"):
    response = get_response(user_input)
    st.write(response)