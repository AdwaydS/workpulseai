"""Audit log page."""

import streamlit as st

from components.theme import render_header
from components.tables import render_data_table
from utils.session import get_db_session, has_role
from services.audit_service import AuditService


def render():
    if not has_role("admin"):
        st.warning("Admin access required.")
        return

    render_header()
    db = get_db_session()

    try:
        svc = AuditService(db)
        logs = svc.get_logs(limit=200)
        rows = [{
            "Time": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "User ID": log.user_id or "System",
            "Action": log.action,
            "Entity": f"{log.entity_type}:{log.entity_id}" if log.entity_type else "",
            "IP": log.ip_address or "",
            "Details": str(log.details or ""),
        } for log in logs]

        render_data_table(rows, "Audit Log", "audit", show_export=True)

    finally:
        db.close()
