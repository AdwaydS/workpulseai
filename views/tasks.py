"""Tasks management page."""

import streamlit as st

from components.theme import render_header
from components.tables import render_data_table
from database.models import TaskStatus, Priority
from utils.session import get_db_session, has_role
from services.task_service import TaskService
from services.project_service import ProjectService
from services.user_service import UserService


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        task_svc = TaskService(db)
        proj_svc = ProjectService(db)

        tab1, tab2 = st.tabs(["📋 My Tasks", "➕ Assign Task"])

        with tab1:
            if has_role("admin", "manager"):
                rows = task_svc.to_dataframe_rows()
            else:
                tasks = task_svc.get_user_tasks(user["id"])
                rows = [{
                    "Project": t.project.name if t.project else "",
                    "Title": t.title,
                    "Status": t.status.value if hasattr(t.status, "value") else str(t.status),
                    "Priority": t.priority.value if hasattr(t.priority, "value") else str(t.priority),
                    "Due": t.due_date.isoformat() if t.due_date else "",
                    "Progress": f"{t.completion_percentage}%",
                } for t in tasks]

            render_data_table(rows, "Tasks", "tasks", show_export=True)

            if not has_role("admin", "manager"):
                st.subheader("Update Task Progress")
                tasks = task_svc.get_user_tasks(user["id"])
                for t in tasks[:5]:
                    new_progress = st.slider(f"{t.title}", 0, 100, int(t.completion_percentage), key=f"prog_{t.id}")
                    if st.button(f"Update {t.title}", key=f"btn_{t.id}"):
                        task_svc.update_progress(t.id, new_progress)
                        st.rerun()

        with tab2:
            if has_role("manager", "admin"):
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                projects = proj_svc.get_all()
                users = UserService(db).get_all()
                with st.form("assign_task"):
                    project = st.selectbox("Project", projects, format_func=lambda p: p.name)
                    title = st.text_input("Task Title*")
                    assignee = st.selectbox("Assign To", users, format_func=lambda u: u.full_name)
                    priority = st.selectbox("Priority", [p.value for p in Priority])
                    status = st.selectbox("Status", [s.value for s in TaskStatus])
                    if st.form_submit_button("Assign Task"):
                        if title and project:
                            task_svc.create({
                                "project_id": project.id,
                                "title": title,
                                "assignee_id": assignee.id,
                                "created_by": user["id"],
                                "priority": Priority(priority),
                                "status": TaskStatus(status),
                            })
                            st.success(f"Task '{title}' assigned!")
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
