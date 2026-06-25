"""Departments and teams management."""

import streamlit as st

from components.theme import render_header
from components.tables import render_data_table
from utils.session import get_db_session, has_role
from services.department_service import DepartmentService, TeamService


def render():
    if not has_role("admin"):
        st.warning("Admin access required.")
        return

    render_header()
    db = get_db_session()

    try:
        dept_svc = DepartmentService(db)
        team_svc = TeamService(db)

        tab1, tab2, tab3 = st.tabs(["🏢 Departments", "👥 Teams", "➕ Create"])

        with tab1:
            render_data_table(dept_svc.to_dataframe_rows(), "Departments", "depts", show_export=True)

        with tab2:
            render_data_table(team_svc.to_dataframe_rows(), "Teams", "teams", show_export=True)

        with tab3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            with st.form("create_dept"):
                st.subheader("New Department")
                name = st.text_input("Department Name")
                desc = st.text_area("Description")
                if st.form_submit_button("Create Department"):
                    if name:
                        dept_svc.create(name, desc)
                        st.success(f"Department '{name}' created!")
                        st.rerun()

            with st.form("create_team"):
                st.subheader("New Team")
                tname = st.text_input("Team Name")
                depts = dept_svc.get_all()
                dept = st.selectbox("Department", depts, format_func=lambda d: d.name)
                if st.form_submit_button("Create Team"):
                    if tname:
                        team_svc.create(tname, dept.id)
                        st.success(f"Team '{tname}' created!")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
