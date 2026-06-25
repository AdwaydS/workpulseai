"""Main Streamlit application entry point."""

import streamlit as st

from components.theme import load_css, toggle_theme
from utils.session import init_session_state, logout_user, has_role

st.set_page_config(
    page_title="WORKPULSE AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
load_css()

if not st.session_state.get("authenticated"):
    from views.login import render as render_login
    render_login()
    st.stop()

# Sidebar navigation
with st.sidebar:
    import os
    import base64
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align:center;padding:1rem 0;"><img src="data:image/png;base64,{b64}" style="width:80px;border-radius:16px;"/></div>', unsafe_allow_html=True)
    st.markdown("### WORKPULSE AI")
    st.caption("Workforce Intelligence Platform")

    user = st.session_state.get("user", {})
    st.markdown(f"**{user.get('full_name', 'User')}**")
    st.caption(f"Role: {user.get('role', '').title()}")

    unread = st.session_state.get("unread_notifications", 0)
    if unread:
        st.markdown(f"🔔 **{unread}** new notifications")

    st.divider()

    role = user.get("role", "employee")
    nav_items = ["Dashboard"]

    if role in ("employee", "manager", "admin"):
        nav_items += ["Attendance", "Work Logs", "Projects", "Tasks", "Kanban", "Calendar", "Notifications"]
    if role in ("manager", "admin"):
        nav_items += ["Team", "Reports"]
    if role == "admin":
        nav_items += ["Users", "Departments", "Analytics", "AI Insights", "Settings", "Audit Log"]
    else:
        nav_items += ["Analytics", "AI Insights", "Reports"]

    page = st.radio("Navigation", nav_items, label_visibility="collapsed")

    st.divider()
    if st.button("🌓 Toggle Theme"):
        toggle_theme()
        st.rerun()
    if st.button("🚪 Logout"):
        logout_user()
        st.rerun()

# Route pages
if page == "Dashboard":
    if has_role("admin"):
        from dashboard.admin_dashboard import render
    elif has_role("manager"):
        from dashboard.manager_dashboard import render
    else:
        from dashboard.employee_dashboard import render
    render()

elif page == "Attendance":
    from views import attendance as attendance_page
    attendance_page.render()

elif page == "Work Logs":
    from views import worklogs as worklogs_page
    worklogs_page.render()

elif page == "Projects":
    from views import projects as projects_page
    projects_page.render()

elif page == "Tasks":
    from views import tasks as tasks_page
    tasks_page.render()

elif page == "Kanban":
    from views import kanban as kanban_page
    kanban_page.render()

elif page == "Calendar":
    from views import calendar as calendar_page
    calendar_page.render()

elif page == "Notifications":
    from views import notifications as notifications_page
    notifications_page.render()

elif page == "Team":
    from views import team as team_page
    team_page.render()

elif page == "Users":
    from views import users as users_page
    users_page.render()

elif page == "Departments":
    from views import departments as dept_page
    dept_page.render()

elif page == "Analytics":
    from views import analytics as analytics_page
    analytics_page.render()

elif page == "AI Insights":
    from views import ai_insights as ai_page
    ai_page.render()

elif page == "Reports":
    from views import reports as reports_page
    reports_page.render()

elif page == "Settings":
    from views import settings as settings_page
    settings_page.render()

elif page == "Audit Log":
    from views import audit as audit_page
    audit_page.render()
