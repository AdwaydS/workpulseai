"""Team management page."""

import streamlit as st

from components.theme import render_header
from components.tables import render_data_table
from components.charts import radar_chart
from utils.session import get_db_session, has_role
from services.user_service import UserService
from services.attendance_service import AttendanceService
from analytics.analytics_service import AnalyticsService


def render():
    if not has_role("manager", "admin"):
        st.warning("Manager access required.")
        return

    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        user_svc = UserService(db)
        att_svc = AttendanceService(db)
        analytics = AnalyticsService(db)

        team_id = user.get("team_id")
        members = user_svc.get_team_members(team_id) if team_id else user_svc.get_all()

        rows = [{
            "Employee ID": m.employee_id,
            "Name": m.full_name,
            "Email": m.email,
            "Role": m.role.name.value if m.role else "",
            "Job Title": m.job_title or "",
            "Weekly Hours": f"{att_svc.get_weekly_hours(m.id):.1f}h",
            "Productivity": analytics.calculate_productivity_score(m.id),
        } for m in members]

        render_data_table(rows, "Team Members", "team", show_export=True)

        if team_id:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Team Performance")
            radar_chart(analytics.team_performance_radar(team_id))
            st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
