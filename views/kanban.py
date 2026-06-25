"""Kanban board page."""

import streamlit as st

from components.theme import render_header
from database.models import TaskStatus
from utils.session import get_db_session
from services.task_service import TaskService
from services.project_service import ProjectService


COLUMN_LABELS = {
    "backlog": "📥 Backlog",
    "todo": "📌 To Do",
    "in_progress": "🔄 In Progress",
    "review": "👀 Review",
    "testing": "🧪 Testing",
    "completed": "✅ Completed",
}


def render():
    render_header()
    db = get_db_session()

    try:
        task_svc = TaskService(db)
        proj_svc = ProjectService(db)
        projects = proj_svc.get_all()

        if not projects:
            st.info("No projects available. Create a project first.")
            return

        selected = st.selectbox("Select Project", projects, format_func=lambda p: p.name)
        board = task_svc.get_kanban_board(selected.id)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        cols = st.columns(6)
        for i, status in enumerate(TaskService.KANBAN_COLUMNS):
            with cols[i]:
                label = COLUMN_LABELS.get(status.value, status.value)
                tasks = board.get(status.value, [])
                st.markdown(f"**{label}** ({len(tasks)})")
                for task in tasks:
                    priority_color = {"critical": "#EF4444", "high": "#F59E0B", "medium": "#6366F1", "low": "#10B981"}
                    p = task.priority.value if hasattr(task.priority, "value") else str(task.priority)
                    color = priority_color.get(p, "#6366F1")
                    assignee = task.assignee.full_name if task.assignee else "Unassigned"
                    st.markdown(f"""
                    <div class="kanban-task" style="border-left:3px solid {color};">
                        <strong>{task.title}</strong><br>
                        <small style="color:var(--text-secondary);">{assignee} · {task.completion_percentage:.0f}%</small>
                    </div>
                    """, unsafe_allow_html=True)

                    statuses = list(TaskStatus)
                    current_idx = statuses.index(task.status) if task.status in statuses else 0
                    move_cols = st.columns(2)
                    with move_cols[0]:
                        if current_idx > 0 and st.button("◀", key=f"left_{task.id}"):
                            task_svc.update_status(task.id, statuses[current_idx - 1])
                            st.rerun()
                    with move_cols[1]:
                        if current_idx < len(statuses) - 1 and st.button("▶", key=f"right_{task.id}"):
                            task_svc.update_status(task.id, statuses[current_idx + 1])
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
