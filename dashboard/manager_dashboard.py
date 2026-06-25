"""Manager dashboard."""

import streamlit as st

from components.cards import kpi_row, ai_insight_card
from components.charts import radar_chart, bar_chart, heatmap_chart
from components.theme import render_header
from utils.session import get_db_session
from services.attendance_service import AttendanceService
from services.user_service import UserService
from services.project_service import ProjectService
from analytics.analytics_service import AnalyticsService
from ai_engine.insights_engine import AIInsightsEngine


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        user_svc = UserService(db)
        att_svc = AttendanceService(db)
        proj_svc = ProjectService(db)
        analytics = AnalyticsService(db)
        ai = AIInsightsEngine(db)

        team_id = user.get("team_id")
        team_members = user_svc.get_team_members(team_id) if team_id else []
        att_stats = att_svc.get_attendance_stats(team_id=team_id)
        proj_stats = proj_svc.get_project_stats()
        radar_data = analytics.team_performance_radar(team_id) if team_id else {}
        insights = ai.generate_insights(team_id=team_id)[:4]

        kpi_row([
            ("Team Size", str(len(team_members)), "Active members", "primary"),
            ("Attendance Rate", f"{att_stats.get('percentage', 0)}%", "This month", "success"),
            ("Active Projects", str(proj_stats.get("in_progress", 0)), f"Total: {proj_stats.get('total', 0)}", "accent"),
            ("Avg Progress", f"{proj_stats.get('avg_progress', 0)}%", "All projects", "warning"),
        ])

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🎯 Team Performance Radar")
            radar_chart(radar_data, "Team Performance")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📊 Department Comparison")
            dept_df = analytics.department_comparison()
            bar_chart(dept_df, "Department", "Utilization", "Resource Utilization by Department")
            st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🔥 Workload Heatmap")
            heatmap = analytics.workload_heatmap(team_id)
            heatmap_chart(heatmap)
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🤖 Team AI Insights")
            for insight in insights:
                ai_insight_card(insight)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("👥 Team Attendance Today")
        if team_id:
            team_att = att_svc.get_team_attendance(team_id)
            for att in team_att:
                status = att.status.value.replace("_", " ").title() if hasattr(att.status, "value") else str(att.status)
                st.markdown(f"**{att.user.full_name}** — {status} · {att.working_hours:.1f}h")
        st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
