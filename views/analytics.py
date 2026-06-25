"""Advanced analytics page."""

import streamlit as st

from components.theme import render_header
from components.charts import (
    line_chart, area_chart, donut_chart, bar_chart,
    radar_chart, treemap_chart, gantt_chart, heatmap_chart, leaderboard_chart,
)
from utils.session import get_db_session
from analytics.analytics_service import AnalyticsService
from services.project_service import ProjectService


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        analytics = AnalyticsService(db)
        proj_svc = ProjectService(db)
        user_id = user["id"] if user.get("role") == "employee" else None
        team_id = user.get("team_id")

        st.markdown("### 📊 Advanced Analytics Dashboard")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Productivity Trend")
            line_chart(analytics.productivity_trend(user_id), "Date", "Hours")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Attendance Trend")
            area_chart(analytics.attendance_trend(), "Date", "Present")
            st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Hours Distribution")
            donut_chart(analytics.hours_distribution(user_id), "Project", "Hours")
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Department Comparison")
            bar_chart(analytics.department_comparison(), "Department", "Utilization")
            st.markdown('</div>', unsafe_allow_html=True)

        c5, c6 = st.columns(2)
        with c5:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Team Performance")
            if team_id:
                radar_chart(analytics.team_performance_radar(team_id))
            else:
                radar_chart(analytics.team_performance_radar(1) if team_id is None else {})
            st.markdown('</div>', unsafe_allow_html=True)

        with c6:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Employee Ranking")
            leaderboard_chart(analytics.employee_ranking())
            st.markdown('</div>', unsafe_allow_html=True)

        c7, c8 = st.columns(2)
        with c7:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Resource Utilization")
            util = analytics.resource_utilization()
            if not util.empty:
                treemap_chart(util, ["Department"], "Hours")
            st.markdown('</div>', unsafe_allow_html=True)

        with c8:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Workload Heatmap")
            heatmap_chart(analytics.workload_heatmap(team_id))
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Project Gantt Chart")
        gantt_chart(proj_svc.get_gantt_data())
        st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
