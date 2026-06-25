"""Attendance management page."""

from datetime import date, timedelta

import streamlit as st

from components.theme import render_header
from components.tables import render_data_table
from components.cards import kpi_row, status_badge
from utils.session import get_db_session, has_role
from services.attendance_service import AttendanceService
from database.models import AttendanceStatus


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        svc = AttendanceService(db)
        stats = svc.get_attendance_stats(user["id"])
        weekly = svc.get_weekly_hours(user["id"])
        monthly = svc.get_monthly_hours(user["id"])
        today = svc.get_today(user["id"])

        kpi_row([
            ("Today Status", today.status.value.replace("_", " ").title() if today else "Not Marked", "", "primary"),
            ("Weekly Hours", f"{weekly:.1f}h", "", "accent"),
            ("Monthly Hours", f"{monthly:.1f}h", "", "success"),
            ("Overtime", f"{stats.get('overtime_hours', 0):.1f}h", "This month", "warning"),
        ])

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📋 My Attendance", "✅ Mark Status", "📊 Team View"])

        with tab1:
            start = date.today() - timedelta(days=30)
            records = svc.get_user_attendance(user["id"], start, date.today())
            rows = [{
                "Date": r.date.isoformat(),
                "Login": str(r.login_time) if r.login_time else "",
                "Logout": str(r.logout_time) if r.logout_time else "",
                "Status": r.status.value if hasattr(r.status, "value") else str(r.status),
                "Hours": r.working_hours,
                "Overtime": r.overtime_hours,
                "IP": r.ip_address or "",
                "Device": r.device or "",
            } for r in records]
            render_data_table(rows, "Attendance Records", "attendance", show_export=True)

        with tab2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Mark Attendance Status")
            status = st.selectbox("Status", [s.value for s in AttendanceStatus])
            if st.button("Submit Status"):
                svc.mark_status(user["id"], AttendanceStatus(status))
                st.success(f"Status marked as {status.replace('_', ' ').title()}")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            if has_role("manager", "admin"):
                team_id = user.get("team_id")
                if team_id:
                    team_att = svc.get_team_attendance(team_id)
                    rows = [{
                        "Employee": a.user.full_name,
                        "Date": a.date.isoformat(),
                        "Status": a.status.value if hasattr(a.status, "value") else str(a.status),
                        "Hours": a.working_hours,
                        "Approved": a.approved,
                    } for a in team_att]
                    render_data_table(rows, "Team Attendance Today", "team_att")

                    st.subheader("Approve Attendance")
                    pending = [a for a in team_att if not a.approved]
                    for att in pending:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{att.user.full_name}** — {att.date}")
                        with col2:
                            if st.button("Approve", key=f"approve_{att.id}"):
                                svc.approve_attendance(att.id, user["id"])
                                db.commit()
                                st.rerun()
                else:
                    st.info("No team assigned.")
            else:
                st.warning("Manager access required.")

    finally:
        db.close()
