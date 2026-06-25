"""Work logs page."""

from datetime import date, datetime, time

import streamlit as st

from components.theme import render_header
from components.tables import render_data_table
from database.models import Priority
from utils.session import get_db_session
from services.worklog_service import WorkLogService


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        svc = WorkLogService(db)

        tab1, tab2 = st.tabs(["📝 New Work Log", "📋 Work Log History"])

        with tab1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            with st.form("worklog_form"):
                c1, c2 = st.columns(2)
                with c1:
                    project_name = st.text_input("Project Name")
                    task_name = st.text_input("Task Name")
                    priority = st.selectbox("Priority", [p.value for p in Priority])
                with c2:
                    hours = st.number_input("Hours Spent", min_value=0.1, max_value=24.0, value=1.0, step=0.5)
                    completion = st.slider("Completion %", 0, 100, 50)
                    log_date = st.date_input("Date", value=date.today())
                description = st.text_area("Description")
                notes = st.text_area("Notes")

                if st.form_submit_button("Save Work Log", use_container_width=True):
                    svc.create({
                        "user_id": user["id"],
                        "project_name": project_name,
                        "task_name": task_name,
                        "description": description,
                        "priority": Priority(priority),
                        "hours_spent": hours,
                        "completion_percentage": completion,
                        "notes": notes,
                        "log_date": log_date,
                        "start_time": datetime.combine(log_date, time(9, 0)),
                        "end_time": datetime.combine(log_date, time(9 + int(hours), 0)),
                    })
                    st.success("Work log saved!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            rows = svc.to_dataframe_rows(user["id"])
            render_data_table(
                rows, "Work Logs", "worklogs",
                show_export=True, show_import=True,
                import_handler=lambda r: svc.import_from_rows(user["id"], r),
                template_type="work_logs",
            )

    finally:
        db.close()
