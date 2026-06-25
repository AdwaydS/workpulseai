"""System settings page."""

import streamlit as st

from components.theme import render_header
from utils.session import get_db_session, has_role
from database.models import SystemSetting
from config.settings import get_settings


def render():
    if not has_role("admin"):
        st.warning("Admin access required.")
        return

    render_header()
    settings = get_settings()
    db = get_db_session()

    try:
        st.markdown("### ⚙️ System Settings")

        tab1, tab2 = st.tabs(["General", "Database"])

        with tab1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            sys_settings = db.query(SystemSetting).all()
            for s in sys_settings:
                new_val = st.text_input(s.key.replace("_", " ").title(), value=s.value or "", key=f"setting_{s.id}")
                if st.button(f"Save {s.key}", key=f"save_{s.id}"):
                    s.value = new_val
                    db.commit()
                    st.success(f"Updated {s.key}")

            st.divider()
            st.subheader("Attendance Configuration")
            st.info(f"Work Start: {settings.work_start_hour:02d}:{settings.work_start_minute:02d}")
            st.info(f"Late Threshold: {settings.late_threshold_minutes} minutes")
            st.info(f"Standard Hours: {settings.standard_work_hours}")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.code(settings.database_url.replace(settings.database_url.split("@")[0].split("//")[1], "****"), language="text")
            st.info(f"Pool Size: {settings.db_pool_size} | Max Overflow: {settings.db_max_overflow}")
            st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
