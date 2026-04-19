import streamlit as st
from datetime import datetime, timedelta
from groq import Groq



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

# ---------------- AI FUNCTION ----------------
def ai_response(user_input, events):
    try:
        schedule_text = "\n".join(
            [f"{e['title']} ({e['start']} - {e['end']})" for e in events]
        ) if events else "No events"

        prompt = f"""
You are a smart timetable assistant.

User schedule:
{schedule_text}

User request:
{user_input}

Give a clear, helpful answer.
If it's a study plan, include time slots.
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
if st.button("🚀 Create Event"):
    if start >= end:
        st.error("⚠️ End time must be greater than Start time")
    else:
        new_event = {
            "title": title,
            "start": start,
            "end": end
        }

        # ✅ DUPLICATE CHECK
        for event in st.session_state.events:
            if start == event["start"] and end == event["end"]:
                st.warning("⚠️ This exact event already exists")
                st.stop()

        # ✅ CONFLICT CHECK
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
st.header("📅 Schedule (Calendar View)")

from streamlit_calendar import calendar

calendar_events = []

for e in st.session_state.events:
    calendar_events.append({
        "title": e["title"],
        "start": e["start"].isoformat(),
        "end": e["end"].isoformat(),
    })

calendar(events=calendar_events)

# ---------------- FREE TIME ----------------
from datetime import datetime, timedelta

st.header("🕒 Free Time Finder")

if st.button("Find Free Time"):
    events = sorted(st.session_state.events, key=lambda x: x["start"])

    if not events:
        st.write("🟢 Full day is free!")
    
    else:
        found = False

        # ✅ 👉 ADD HERE
        start_day = datetime.combine(events[0]["start"].date(), datetime.min.time())
        end_day = datetime.combine(events[-1]["end"].date(), datetime.max.time())

        # ---- Before first event ----
        if start_day < events[0]["start"]:
            st.write(f"🟢 Free: {start_day} → {events[0]['start']}")
            found = True

        # ---- Between events ----
        for i in range(len(events) - 1):
            if events[i]["end"] < events[i+1]["start"]:
                st.write(f"🟢 Free: {events[i]['end']} → {events[i+1]['start']}")
                found = True

        # ---- After last event ----
        if events[-1]["end"] < end_day:
            st.write(f"🟢 Free: {events[-1]['end']} → {end_day}")
            found = True

        if not free_slots:
            st.error("⚠️ No free time available")
        else:
            # show all
            for s, e in free_slots:
                st.write(f"🟢 {s.strftime('%H:%M')} → {e.strftime('%H:%M')}")

            # 🔥 highlight best slot
            best = max(free_slots, key=lambda x: x[1] - x[0])
            st.success(
                f"⭐ Best Slot: {best[0].strftime('%H:%M')} → {best[1].strftime('%H:%M')}"
            )

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
        if st.button("⚡ Auto Generate Study Plan"):
    if not st.session_state.events:
        st.warning("Add some events first")
    else:
        response = ai_response(
            "Create a full study timetable from my free time",
            st.session_state.events
        )
        st.success(response)
# ---------------- FOOTER ----------------
st.markdown("---")
