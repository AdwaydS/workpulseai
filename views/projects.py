"""Projects management page."""

import streamlit as st

from components.theme import render_header
from components.tables import render_data_table
from components.cards import kpi_row
from database.models import ProjectStatus
from utils.session import get_db_session, has_role
from services.project_service import ProjectService


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        svc = ProjectService(db)
        stats = svc.get_project_stats()

        kpi_row([
            ("Total Projects", str(stats["total"]), "", "primary"),
            ("In Progress", str(stats["in_progress"]), "", "accent"),
            ("Completed", str(stats["completed"]), "", "success"),
            ("Delayed", str(stats["delayed"]), "", "warning"),
        ])

        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📋 All Projects", "➕ Create Project"])

        with tab1:
            if has_role("employee"):
                projects = svc.get_user_projects(user["id"])
                rows = [{
                    "Name": p.name, "Client": p.client_name or "",
                    "Status": p.status.value if hasattr(p.status, "value") else str(p.status),
                    "Progress": f"{p.progress_percentage}%",
                    "Deadline": p.deadline.isoformat() if p.deadline else "",
                    "Hours": f"{p.consumed_hours}/{p.allocated_hours}",
                } for p in projects]
            else:
                rows = svc.to_dataframe_rows()

            import_handler = svc.import_from_rows if has_role("manager", "admin") else None
            render_data_table(
                rows, "Projects", "projects",
                show_export=True,
                show_import=has_role("manager", "admin"),
                import_handler=import_handler,
                template_type="projects",
            )

        with tab2:
            if has_role("manager", "admin"):
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                with st.form("create_project"):
                    c1, c2 = st.columns(2)
                    with c1:
                        name = st.text_input("Project Name*")
                        client = st.text_input("Client Name")
                        budget = st.number_input("Budget", min_value=0.0, value=0.0)
                    with c2:
                        status = st.selectbox("Status", [s.value for s in ProjectStatus])
                        progress = st.slider("Progress %", 0, 100, 0)
                        alloc_hours = st.number_input("Allocated Hours", min_value=0.0, value=40.0)
                    if st.form_submit_button("Create Project"):
                        if name:
                            svc.create({
                                "name": name, "client_name": client, "budget": budget,
                                "status": ProjectStatus(status), "progress_percentage": progress,
                                "allocated_hours": alloc_hours, "manager_id": user["id"],
                            })
                            st.success(f"Project '{name}' created!")
                            st.rerun()
                        else:
                            st.error("Project name is required.")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Contact your manager to create projects.")

    finally:
        db.close()
