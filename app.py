import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Timetable AI", layout="wide")

# ---------------- TITLE ----------------
st.markdown("""
# 📅 Smart Timetable Assistant AI
### 🚀 AI-powered Smart Scheduling for Students
---
""")

# ---------------- STORAGE ----------------
if "events" not in st.session_state:
    st.session_state.events = []

# ---------------- ADD EVENT ----------------
st.header("➕ Add Event")

col1, col2 = st.columns(2)

with col1:
    title = st.text_input("📌 Event Title")

with col2:
    start = st.time_input("⏰ Start Time")

end = st.time_input("⏳ End Time")

if st.button("🚀 Create Event"):
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
        st.error("⚠️ Conflict detected! Choose another time.")
    else:
        st.session_state.events.append(new_event)
        st.success("✅ Event added successfully!")
        st.balloons()

# ---------------- VIEW EVENTS ----------------
st.header("📅 Your Schedule")

if st.session_state.events:
    for event in st.session_state.events:
        st.markdown(f"""
        ### 📌 {event['title']}
        🕒 {event['start']} → {event['end']}
        ---
        """)
else:
    st.write("No events added yet")

# ---------------- FREE TIME FINDER ----------------
st.header("🕒 Find Free Time")

if st.button("Find Free Slots"):
    events = sorted(st.session_state.events, key=lambda x: x["start"])

    if len(events) < 2:
        st.write("Not enough events to find free time")
    else:
        for i in range(len(events) - 1):
            st.write(f"🟢 Free: {events[i]['end']} → {events[i+1]['start']}")

# ---------------- AI ASSISTANT ----------------
st.header("🤖 AI Smart Assistant")

user_input = st.text_input("Ask something (e.g., Plan my study time)")

if st.button("Ask AI"):
    if user_input:
        st.success(f"💡 Suggestion: Try scheduling '{user_input}' in your free time with proper breaks.")

# ---------------- FOOTER ----------------
st.markdown("""
---
✨ Built with ❤️ for Hackathon
""")
