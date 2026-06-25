"""Admin dashboard."""

import streamlit as st

from components.cards import kpi_row, ai_insight_card
from components.charts import area_chart, treemap_chart, gantt_chart, leaderboard_chart
from components.theme import render_header
from utils.session import get_db_session
from services.user_service import UserService
from services.project_service import ProjectService
from services.task_service import TaskService
from services.attendance_service import AttendanceService
from analytics.analytics_service import AnalyticsService
from ai_engine.insights_engine import AIInsightsEngine


def render():
    render_header()
    db = get_db_session()

    try:
        user_svc = UserService(db)
        proj_svc = ProjectService(db)
        task_svc = TaskService(db)
        att_svc = AttendanceService(db)
        analytics = AnalyticsService(db)
        ai = AIInsightsEngine(db)

        org = user_svc.get_org_stats()
        proj_stats = proj_svc.get_project_stats()
        total_tasks = len(task_svc.to_dataframe_rows())
        att_stats = att_svc.get_attendance_stats()
        health = analytics.org_health_score()
        insights = ai.generate_insights()[:5]

        kpi_row([
            ("Total Employees", str(org["total_employees"]), f"Active: {org['active_employees']}", "primary"),
            ("Attendance", f"{att_stats.get('percentage', 0)}%", "Organization-wide", "success"),
            ("Projects", str(proj_stats["total"]), f"In Progress: {proj_stats['in_progress']}", "accent"),
            ("Health Score", f"{health}", "Org health / 100", "warning"),
        ])

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📈 Attendance Trend")
            att_trend = analytics.attendance_trend()
            area_chart(att_trend, "Date", "Present", "Daily Attendance")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🏆 Employee Ranking")
            ranking = analytics.employee_ranking()
            leaderboard_chart(ranking)
            st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🌳 Resource Utilization")
            util = analytics.resource_utilization()
            if not util.empty:
                treemap_chart(util, ["Department"], "Hours", "Department Hours")
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📅 Project Gantt")
            gantt_chart(proj_svc.get_gantt_data())
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🤖 Organization AI Insights")
        for insight in insights:
            ai_insight_card(insight)
        st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
