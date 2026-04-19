import streamlit as st
import os
from datetime import datetime
import google.generativeai as genai
import streamlit as st

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
else:
    model = None

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Timetable AI", layout="wide")

USE_GOOGLE = os.getenv("USE_GOOGLE", "false") == "true"

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash-latest")

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

col1, col2 = st.columns(2)

with col1:
    title = st.text_input("Event Title")

with col2:
    start = st.time_input("Start Time")

end = st.time_input("End Time")

if st.button("🚀 Create Event"):
    new_event = {"title": title, "start": start, "end": end}

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
st.header("🕒 Free Time Finder")

if st.button("Find Free Time"):
    if not USE_GOOGLE:
        events = sorted(st.session_state.events, key=lambda x: x["start"])

        if len(events) < 2:
            st.write("Not enough events")
        else:
            for i in range(len(events)-1):
                st.write(f"Free: {events[i]['end']} → {events[i+1]['start']}")
    else:
        st.info("Free time works best in local mode")

# ---------------- GEMINI AI ----------------
st.header("🤖 AI Assistant")

user_input = st.text_input("Ask something")

if st.button("Ask AI"):
    if not model:
        st.error("AI not configured")
    elif user_input:
        try:
            prompt = f"""
            User schedule: {st.session_state.events}

            User request: {user_input}

            Suggest best free time and advice.
            """
            response = model.generate_content(prompt)
            st.success(response.text)
        except Exception as e:
            st.error(f"AI Error: {e}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.write("✨ Hackathon Project")
