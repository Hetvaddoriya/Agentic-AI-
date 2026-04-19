import streamlit as st
from datetime import time
import requests

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

Create a helpful response and study plan with proper time slots.
"""

        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn""
        headers = {
            "Authorization": f"Bearer {st.secrets.get('HF_API_KEY', '')}"
        }

        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=20
        )

        # ✅ Check HTTP error
        if response.status_code != 200:
            return f"❌ API Error {response.status_code}: {response.text}"

        # ✅ Safe JSON parse
        try:
            result = response.json()
        except:
            return "⚠️ AI returned invalid response. Try again."

        # ✅ Handle loading / empty
        if isinstance(result, dict) and "error" in result:
            return f"⚠️ {result['error']}"

        if not result:
            return "⚠️ No response from AI. Try again."

        # ✅ Final output
        return result[0].get("generated_text", "⚠️ No text generated")

    except Exception as e:
        return f"❌ AI Error: {e}"

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

        conflict_event = None

        for event in st.session_state.events:
            if (start < event["end"] and end > event["start"]):
                conflict_event = event
                break

        if conflict_event:
            st.error(
                f"⚠️ Conflict with '{conflict_event['title']}' "
                f"({conflict_event['start']} → {conflict_event['end']}) ❌"
            )
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

        if events[0]["start"] > time(0, 0):
            st.write(f"🟢 Free: 00:00 → {events[0]['start']}")
            found = True

        for i in range(len(events) - 1):
            if events[i]["end"] < events[i+1]["start"]:
                st.write(f"🟢 Free: {events[i]['end']} → {events[i+1]['start']}")
                found = True

        if events[-1]["end"] < time(23, 59):
            st.write(f"🟢 Free: {events[-1]['end']} → 23:59")
            found = True

        if not found:
            st.write("⚠️ No free time available")

# ---------------- AI ASSISTANT ----------------
st.header("🤖 Smart Assistant")

user_input = st.text_input("Ask something (e.g., create study plan)")

if st.button("Ask AI"):
    if not user_input:
        st.warning("Please enter a question")
    else:
        with st.spinner("Thinking..."):
            response = ai_response(user_input, st.session_state.events)
        st.success(response)

# ---------------- FOOTER ----------------
st.markdown("---")
