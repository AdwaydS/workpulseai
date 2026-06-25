"""Session state and application utilities."""

import os
from datetime import datetime
from typing import Optional

import streamlit as st
from user_agents import parse

from database.connection import SessionLocal
from authentication.auth_service import AuthService
from services.notification_service import NotificationService


def init_session_state():
    defaults = {
        "authenticated": False,
        "user": None,
        "token": None,
        "session_id": None,
        "theme": "dark",
        "current_page": "Dashboard",
        "unread_notifications": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_db_session():
    return SessionLocal()


def get_client_info() -> dict:
    headers = st.context.headers if hasattr(st, "context") else {}
    ua_string = headers.get("User-Agent", "Streamlit/1.0")
    ua = parse(ua_string)
    return {
        "browser": f"{ua.browser.family} {ua.browser.version_string}",
        "device": "Mobile" if ua.is_mobile else ("Tablet" if ua.is_tablet else "Desktop"),
        "ip_address": headers.get("X-Forwarded-For", headers.get("Remote-Addr", "127.0.0.1")),
        "location": "Office HQ",
    }


def login_user(email: str, password: str) -> bool:
    db = get_db_session()
    try:
        auth = AuthService(db)
        client = get_client_info()
        result = auth.authenticate(email, password, **client)
        if result:
            st.session_state.authenticated = True
            st.session_state.user = result.user
            st.session_state.token = result.access_token
            st.session_state.session_id = result.user.get("session_id")
            notif_svc = NotificationService(db)
            st.session_state.unread_notifications = notif_svc.get_unread_count(result.user["id"])
            return True
        return False
    finally:
        db.close()


def logout_user():
    if st.session_state.get("user") and st.session_state.get("session_id"):
        db = get_db_session()
        try:
            AuthService(db).logout(st.session_state.user["id"], st.session_state.session_id)
        finally:
            db.close()
    for key in ["authenticated", "user", "token", "session_id"]:
        st.session_state[key] = None if key != "authenticated" else False


def require_auth():
    if not st.session_state.get("authenticated"):
        st.switch_page("pages/0_Login.py") if hasattr(st, "switch_page") else None
        return False
    return True


def has_role(*roles: str) -> bool:
    user = st.session_state.get("user", {})
    return user.get("role", "") in roles


def format_duration(minutes: float) -> str:
    if not minutes:
        return "0h 0m"
    h = int(minutes // 60)
    m = int(minutes % 60)
    return f"{h}h {m}m"


def format_time(t) -> str:
    if not t:
        return "—"
    if isinstance(t, str):
        return t
    return t.strftime("%H:%M")


def get_logo_path() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
