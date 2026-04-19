import streamlit as st
import os
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Timetable AI", layout="wide")

USE_GOOGLE = os.getenv("USE_GOOGLE", "false") == "true"

# ---------------- UI HEADER ----------------
st.markdown("""
# 📅 Smart Timetable Assistant AI
### 🚀 Smart Scheduling + AI Assistant
---
""")

# ---------------- LOCAL STORAGE ----------------
if "events" not in st.session_state:
    st.session_state.events = []

# ---------------- GOOGLE FUNCTIONS (LOCAL ONLY) ----------------
if USE_GOOGLE:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def authenticate_google():
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        return build('calendar', 'v3', credentials=creds)

    def get_events():
        service = authenticate_google()
        events_result = service.events().list(
            calendarId='primary',
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])

    def create_event(summary, start, end):
        service = authenticate_google()
        event = {
            'summary': summary,
            'start': {'dateTime': start.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end.isoformat(), 'timeZone': 'Asia/Kolkata'},
        }
        service.events().insert(calendarId='primary', body=event).execute()

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
            st.error("⚠️ Conflict detected!")
        else:
            st.session_state.events.append(new_event)
            st.success("✅ Event added")
    # -------- GET EVENTS --------
    if USE_GOOGLE:
        try:
            events = get_events()
        except:
            events = []
    else:
        events = st.session_state.events

    # -------- CONFLICT CHECK --------
    conflict = False
    for e in events:
        try:
            if USE_GOOGLE:
                s = datetime.fromisoformat(e['start']['dateTime'])
                en = datetime.fromisoformat(e['end']['dateTime'])
            else:
                s = e["start"]
                en = e["end"]

            if (start < en and end > s):
                conflict = True
                break
        except:
            pass

    if conflict:
        st.error("⚠️ Conflict detected!")
    else:
        if USE_GOOGLE:
            try:
                create_event(title, start, end)
                st.success("✅ Event added to Google Calendar")
            except:
                st.error("❌ Google Calendar failed")
        else:
            st.session_state.events.append(new_event)
            st.success("✅ Event added locally")

# ---------------- VIEW EVENTS ----------------
st.header("📅 Schedule")

if USE_GOOGLE:
    try:
        events = get_events()
    except:
        events = []
else:
    events = st.session_state.events

if events:
    for e in events:
        try:
            if USE_GOOGLE:
                st.write(f"📌 {e['summary']} | {e['start']['dateTime']}")
            else:
                st.write(f"📌 {e['title']} | {e['start']} → {e['end']}")
        except:
            pass
else:
    st.write("No events")

# ---------------- FREE TIME ----------------
from datetime import time

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
# ---------------- GEMINI AI ----------------
st.header("🤖 Smart Assistant")

user_input = st.text_input("Ask something (e.g., when am I free?)")

if st.button("Ask AI"):
    if user_input:
        response = smart_response(user_input, st.session_state.events)
        st.success(response)

# ---------------- FOOTER ----------------
st.markdown("---")
