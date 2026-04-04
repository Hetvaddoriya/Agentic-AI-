import streamlit as st
from datetime import datetime
import os.path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


# -------- AUTH --------

def authenticate_google():
    import streamlit as st

    creds_dict = {
        "installed": {
            "client_id": st.secrets["google"]["client_id"],
            "project_id": st.secrets["google"]["project_id"],
            "auth_uri": st.secrets["google"]["auth_uri"],
            "token_uri": st.secrets["google"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
            "client_secret": st.secrets["google"]["client_secret"],
            "redirect_uris": st.secrets["google"]["redirect_uris"]
        }
    }

    flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
    creds = flow.run_local_server(port=0)

    service = build('calendar', 'v3', credentials=creds)
    return service

# -------- GET EVENTS --------
def get_events():
    service = authenticate_google()

    now = datetime.utcnow().isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return events_result.get('items', [])


# -------- CREATE EVENT --------
def create_event(summary, start_time, end_time):
    service = authenticate_google()

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
    }

    event = service.events().insert(
        calendarId='primary', body=event).execute()

    return event.get('htmlLink')


# -------- CONFLICT CHECK --------
def is_conflict(events, new_start, new_end):
    new_start = datetime.fromisoformat(new_start)
    new_end = datetime.fromisoformat(new_end)

    for event in events:
        start = datetime.fromisoformat(event['start']['dateTime'])
        end = datetime.fromisoformat(event['end']['dateTime'])

        if (new_start < end and new_end > start):
            return True

    return False
import streamlit as st
def get_response(user_input):
    return f"""
    📅 Suggestion:
    - Try scheduling '{user_input}' in your free time
    - Avoid overlapping with existing events
    - Keep buffer time between tasks
    """
from datetime import datetime

st.title("📅 Smart Timetable Assistant AI")

# ---- ADD EVENT ----
st.header("Add Event")

title = st.text_input("Event Title")
start = st.datetime_input("Start Time")
end = st.datetime_input("End Time")

if st.button("Add Event"):
    try:
        events = get_events()
    except:
        events = []
        st.warning("⚠️ Calendar not available in cloud")

    conflict = is_conflict(
        events,
        start.isoformat(),
        end.isoformat()
    )

    if conflict:
        st.error("⚠️ Conflict detected! Choose another time.")
    else:
        try:
    link = create_event(title, start.isoformat(), end.isoformat())
    st.success(f"✅ Event Created: {link}")
except:
    st.error("❌ Cannot create event in cloud")
events = get_events()
try:
    something()
except:
events = []
st.warning("⚠️ Calendar not available in cloud")
    st.warning("⚠️ Calendar not available in cloud")

    conflict = is_conflict(
        events,
        start.isoformat(),
        end.isoformat()
    )

    if conflict:
        st.error("⚠️ Conflict detected! Choose another time.")
    else:
    try:
    link = create_event(title, start.isoformat(), end.isoformat())
    st.success(f"✅ Event Created: {link}")
     except:
     st.error("❌ Cannot create event in cloud")

# ---- VIEW EVENTS ----
st.header("Upcoming Events")

try:
    events = get_events()
except:
    events = []
    st.warning("⚠️ Cannot fetch events in cloud")
for event in events:
    st.write(f"📌 {event['summary']} - {event['start']['dateTime']}")

# ---- AI ASSISTANT ----
st.header("AI Assistant")

user_input = st.text_input("Ask anything (e.g., find free time)")

if st.button("Ask AI"):
    response = get_response(user_input)
    st.write(response)
