"""Reusable KPI card components."""

import streamlit as st


def kpi_card(label: str, value: str, delta: str = "", color: str = "primary"):
    colors = {
        "primary": "linear-gradient(135deg, #6366F1, #4F46E5)",
        "success": "linear-gradient(135deg, #10B981, #059669)",
        "warning": "linear-gradient(135deg, #F59E0B, #D97706)",
        "danger": "linear-gradient(135deg, #EF4444, #DC2626)",
        "accent": "linear-gradient(135deg, #06B6D4, #0891B2)",
    }
    bg = colors.get(color, colors["primary"])
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card" style="background:{bg}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def kpi_row(cards: list):
    cols = st.columns(len(cards))
    for col, (label, value, delta, color) in zip(cols, cards):
        with col:
            kpi_card(label, value, delta, color)


def glass_section(title: str, content_fn):
    st.markdown(f'<div class="glass-card"><h3 style="margin-top:0;font-family:Poppins,sans-serif;">{title}</h3>', unsafe_allow_html=True)
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)


def ai_insight_card(insight: dict):
    severity = insight.get("severity", "info")
    st.markdown(f"""
    <div class="ai-insight ai-insight-{severity}">
        <div style="display:flex;align-items:flex-start;gap:0.75rem;">
            <span style="font-size:1.5rem;">{insight.get('icon', '💡')}</span>
            <div>
                <strong style="color:{insight.get('color', '#6366F1')}">{insight.get('title', '')}</strong>
                <p style="margin:0.25rem 0 0 0;color:var(--text-secondary);font-size:0.9rem;">{insight.get('message', '')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    status_lower = status.lower().replace(" ", "_")
    badge_class = "badge-primary"
    if status_lower in ("completed", "present", "approved"):
        badge_class = "badge-success"
    elif status_lower in ("late", "delayed", "review", "testing"):
        badge_class = "badge-warning"
    elif status_lower in ("absent", "critical", "cancelled"):
        badge_class = "badge-danger"
    return f'<span class="badge {badge_class}">{status.replace("_", " ").title()}</span>'
