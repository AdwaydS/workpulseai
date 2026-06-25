"""UI theme and styling utilities."""

import os
import streamlit as st


def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "theme.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            theme = st.session_state.get("theme", "dark")
            st.markdown(
                f'<style>{f.read()}</style>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<script>document.documentElement.setAttribute("data-theme", "{theme}");</script>',
                unsafe_allow_html=True,
            )


def render_header(show_notifications: bool = True):
    logo_path = "assets/logo.png"
    logo_html = ""
    if os.path.exists(logo_path):
        import base64
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{b64}" class="app-logo" alt="Logo"/>'
    else:
        logo_html = '<div class="app-logo" style="background:linear-gradient(135deg,#6366F1,#06B6D4);display:flex;align-items:center;justify-content:center;font-size:1.2rem;">⚡</div>'

    user = st.session_state.get("user", {})
    unread = st.session_state.get("unread_notifications", 0)
    notif_badge = f'<span class="notification-badge">{unread}</span>' if unread > 0 and show_notifications else ""

    st.markdown(f"""
    <div class="app-header">
        {logo_html}
        <div>
            <div class="app-title">WORKPULSE AI</div>
            <div class="app-subtitle">Intelligent Workforce Management Platform</div>
        </div>
        <div style="margin-left:auto;display:flex;align-items:center;gap:1rem;">
            {notif_badge}
            <span style="color:var(--text-secondary);font-size:0.85rem;">
                {user.get('full_name', 'Guest')} · {user.get('role', '').title()}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def toggle_theme():
    current = st.session_state.get("theme", "dark")
    st.session_state.theme = "light" if current == "dark" else "dark"
