"""Employee dashboard."""

from datetime import datetime, date

import streamlit as st

from components.cards import kpi_row, ai_insight_card
from components.charts import line_chart, donut_chart
from components.theme import render_header
from utils.session import get_db_session, format_time
from services.attendance_service import AttendanceService
from services.worklog_service import WorkLogService
from services.project_service import ProjectService
from services.task_service import TaskService
from analytics.analytics_service import AnalyticsService
from ai_engine.insights_engine import AIInsightsEngine


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        att_svc = AttendanceService(db)
        wl_svc = WorkLogService(db)
        proj_svc = ProjectService(db)
        task_svc = TaskService(db)
        analytics = AnalyticsService(db)
        ai = AIInsightsEngine(db)

        today_att = att_svc.get_today(user["id"])
        weekly_hours = att_svc.get_weekly_hours(user["id"])
        monthly_hours = att_svc.get_monthly_hours(user["id"])
        today_work = wl_svc.get_today_hours(user["id"])
        projects = proj_svc.get_user_projects(user["id"])
        tasks = task_svc.get_user_tasks(user["id"])
        productivity = analytics.calculate_productivity_score(user["id"])
        insights = ai.generate_insights(user_id=user["id"])[:3]

        login_time = format_time(today_att.login_time) if today_att else "—"
        logout_time = format_time(today_att.logout_time) if today_att else "—"
        status = today_att.status.value.replace("_", " ").title() if today_att and hasattr(today_att.status, "value") else "Not Marked"

        kpi_row([
            ("Login Time", login_time, "", "primary"),
            ("Today's Hours", f"{today_work:.1f}h", f"Total: {today_att.working_hours if today_att else 0:.1f}h", "accent"),
            ("Weekly Hours", f"{weekly_hours:.1f}h", "This week", "success"),
            ("Productivity", f"{productivity}", "Score / 100", "warning"),
        ])

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 1])

        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📈 Productivity Trend")
            trend = analytics.productivity_trend(user["id"])
            line_chart(trend, "Date", "Hours", "Daily Hours Logged")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🎯 Work Distribution")
            dist = analytics.hours_distribution(user["id"])
            donut_chart(dist, "Project", "Hours")
            st.markdown('</div>', unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📋 Quick Stats")
            st.metric("Monthly Hours", f"{monthly_hours:.1f}h")
            st.metric("Active Projects", len(projects))
            st.metric("Assigned Tasks", len(tasks))
            st.metric("Attendance", status)
            st.markdown('</div>', unsafe_allow_html=True)

        c4, c5 = st.columns(2)
        with c4:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🕐 Activity Timeline")
            logs = wl_svc.get_user_logs(user["id"])[:8]
            for log in logs:
                st.markdown(f"""
                <div class="timeline-item">
                    <strong>{log.task_name or 'Work Log'}</strong> — {log.project_name or 'N/A'}<br>
                    <small style="color:var(--text-secondary)">{log.log_date} · {log.hours_spent:.1f}h · {log.priority.value if hasattr(log.priority,'value') else log.priority}</small>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c5:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🤖 AI Insights")
            for insight in insights:
                ai_insight_card(insight)
            st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
