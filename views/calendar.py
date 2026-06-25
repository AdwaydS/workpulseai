"""Calendar page."""

from datetime import date

import streamlit as st

from components.theme import render_header
from utils.session import get_db_session
from services.calendar_service import CalendarService


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        svc = CalendarService(db)
        today = date.today()

        tab1, tab2 = st.tabs(["📅 Calendar View", "➕ Add Event"])

        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                year = st.number_input("Year", value=today.year, min_value=2020, max_value=2030)
            with c2:
                month = st.selectbox("Month", list(range(1, 13)), index=today.month - 1)

            events = svc.get_month_events(user["id"], int(year), month)
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            if events:
                for e in events:
                    color = e.get("color", "#6366F1")
                    st.markdown(f"""
                    <div style="border-left:4px solid {color};padding:0.75rem 1rem;margin-bottom:0.5rem;background:var(--bg-card);border-radius:8px;">
                        <strong>{e['title']}</strong><br>
                        <small style="color:var(--text-secondary);">{e['start'][:10]} · {e.get('type', 'event').title()}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No events for this month.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            with st.form("add_event"):
                title = st.text_input("Event Title*")
                event_type = st.selectbox("Type", ["meeting", "deadline", "leave", "holiday", "milestone"])
                event_date = st.date_input("Date")
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
                description = st.text_area("Description")
                if st.form_submit_button("Add Event"):
                    from datetime import datetime
                    if title:
                        svc.create({
                            "user_id": user["id"],
                            "title": title,
                            "event_type": event_type,
                            "start_datetime": datetime.combine(event_date, start_time),
                            "end_datetime": datetime.combine(event_date, end_time),
                            "description": description,
                            "color": "#6366F1",
                        })
                        db.commit()
                        st.success("Event added!")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
