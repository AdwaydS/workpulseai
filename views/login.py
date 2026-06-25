"""Login view."""

import os
import base64
import streamlit as st

from utils.session import login_user


def render():
    logo_path = "assets/logo.png"
    logo_html = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{b64}" style="width:100px;border-radius:20px;margin:0 auto 1rem;display:block;" alt="Logo"/>'

    st.markdown(f"""
    <div class="login-container">
    <div class="login-card">
        {logo_html}
        <h1 style="text-align:center;font-family:Poppins,sans-serif;background:linear-gradient(135deg,#6366F1,#06B6D4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">WORKPULSE AI</h1>
        <p style="text-align:center;color:var(--text-secondary);margin-bottom:2rem;">Intelligent Workforce Management Platform</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="admin@workpulse.ai")
            password = st.text_input("Password", type="password", placeholder="Workpulse@123")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            if submitted:
                if login_user(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        with st.expander("Demo Credentials"):
            st.markdown("""
            | Role | Email | Password |
            |------|-------|----------|
            | Admin | admin@workpulse.ai | Workpulse@123 |
            | Manager | manager@workpulse.ai | Workpulse@123 |
            | Employee | john@workpulse.ai | Workpulse@123 |
            """)
