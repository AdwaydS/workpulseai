"""Notifications center."""

import streamlit as st

from components.theme import render_header
from utils.session import get_db_session
from services.notification_service import NotificationService


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        svc = NotificationService(db)
        unread = svc.get_unread_count(user["id"])
        st.session_state.unread_notifications = unread

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"🔔 Notifications ({unread} unread)")
        with col2:
            if st.button("Mark All Read"):
                svc.mark_all_read(user["id"])
                db.commit()
                st.rerun()

        notifications = svc.get_user_notifications(user["id"])
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        if notifications:
            for n in notifications:
                read_style = "opacity:0.6" if n.is_read else ""
                ntype = n.notification_type.value if hasattr(n.notification_type, "value") else str(n.notification_type)
                st.markdown(f"""
                <div class="ai-insight" style="{read_style}">
                    <strong>{n.title}</strong>
                    <span class="badge badge-primary" style="margin-left:0.5rem;">{ntype.replace('_',' ').title()}</span>
                    <p style="margin:0.25rem 0;color:var(--text-secondary);font-size:0.9rem;">{n.message}</p>
                    <small style="color:var(--text-secondary);">{n.created_at.strftime('%Y-%m-%d %H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)
                if not n.is_read:
                    if st.button("Mark Read", key=f"read_{n.id}"):
                        svc.mark_read(n.id, user["id"])
                        db.commit()
                        st.rerun()
        else:
            st.info("No notifications.")
        st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
