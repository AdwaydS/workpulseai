"""AI Insights page."""

import streamlit as st

from components.theme import render_header
from components.cards import ai_insight_card, kpi_row
from utils.session import get_db_session
from ai_engine.insights_engine import AIInsightsEngine


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        ai = AIInsightsEngine(db)
        team_id = user.get("team_id") if user.get("role") == "manager" else None
        user_id = user["id"] if user.get("role") == "employee" else None
        insights = ai.generate_insights(user_id=user_id, team_id=team_id)

        high = sum(1 for i in insights if i.get("severity") == "high")
        medium = sum(1 for i in insights if i.get("severity") == "medium")
        low = sum(1 for i in insights if i.get("severity") in ("low", "info"))

        kpi_row([
            ("Total Insights", str(len(insights)), "Generated", "primary"),
            ("High Priority", str(high), "Requires action", "danger"),
            ("Medium", str(medium), "Monitor closely", "warning"),
            ("Info", str(low), "Informational", "accent"),
        ])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🤖 AI Workforce Intelligence")
        st.caption("Real-time analysis of productivity, attendance, utilization, and project risks.")

        if insights:
            for insight in insights:
                ai_insight_card(insight)
        else:
            st.success("No critical insights at this time. Workforce metrics look healthy.")
        st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
