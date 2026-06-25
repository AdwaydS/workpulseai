"""User management page (Admin)."""

import streamlit as st

from components.theme import render_header
from components.tables import render_data_table
from utils.session import get_db_session, has_role
from services.user_service import UserService
from database.models import Role


def render():
    if not has_role("admin"):
        st.warning("Admin access required.")
        return

    render_header()
    db = get_db_session()

    try:
        svc = UserService(db)
        roles = db.query(Role).all()

        tab1, tab2 = st.tabs(["👥 Users", "➕ Add User"])

        with tab1:
            rows = svc.to_dataframe_rows()
            render_data_table(
                rows, "Users", "users",
                show_export=True, show_import=True,
                import_handler=svc.import_from_rows,
                template_type="users",
            )

        with tab2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            with st.form("add_user"):
                c1, c2 = st.columns(2)
                with c1:
                    emp_id = st.text_input("Employee ID*")
                    email = st.text_input("Email*")
                    username = st.text_input("Username*")
                    password = st.text_input("Password", value="Workpulse@123")
                with c2:
                    fn = st.text_input("First Name*")
                    ln = st.text_input("Last Name*")
                    role = st.selectbox("Role", roles, format_func=lambda r: r.name.value)
                    title = st.text_input("Job Title")
                if st.form_submit_button("Create User"):
                    if emp_id and email and username and fn and ln:
                        svc.create({
                            "employee_id": emp_id, "email": email, "username": username,
                            "password": password, "first_name": fn, "last_name": ln,
                            "role_id": role.id, "job_title": title,
                        })
                        st.success(f"User {fn} {ln} created!")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
