"""Interactive chart components using Plotly and ECharts."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

CHART_THEME = "plotly_dark"
COLORS = ["#6366F1", "#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]


def line_chart(df: pd.DataFrame, x: str, y: str, title: str = ""):
    if df.empty:
        st.info("No data available for chart.")
        return
    fig = px.line(df, x=x, y=y, title=title, color_discrete_sequence=[COLORS[0]])
    fig.update_layout(
        template=CHART_THEME,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)


def area_chart(df: pd.DataFrame, x: str, y: str, title: str = ""):
    if df.empty:
        st.info("No data available for chart.")
        return
    fig = px.area(df, x=x, y=y, title=title, color_discrete_sequence=[COLORS[2]])
    fig.update_layout(template=CHART_THEME, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
    st.plotly_chart(fig, use_container_width=True)


def donut_chart(df: pd.DataFrame, names: str, values: str, title: str = ""):
    if df.empty:
        st.info("No data available for chart.")
        return
    fig = px.pie(df, names=names, values=values, title=title, hole=0.55, color_discrete_sequence=COLORS)
    fig.update_layout(template=CHART_THEME, paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "", color: str = None):
    if df.empty:
        st.info("No data available for chart.")
        return
    fig = px.bar(df, x=x, y=y, title=title, color=color, color_discrete_sequence=COLORS)
    fig.update_layout(template=CHART_THEME, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
    st.plotly_chart(fig, use_container_width=True)


def radar_chart(data: dict, title: str = "Team Performance"):
    if not data:
        st.info("No data available.")
        return
    categories = list(data.keys())
    values = list(data.values())
    fig = go.Figure(data=go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself", line_color=COLORS[0]))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        template=CHART_THEME,
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
    )
    st.plotly_chart(fig, use_container_width=True)


def treemap_chart(df: pd.DataFrame, path: list, values: str, title: str = ""):
    if df.empty:
        st.info("No data available.")
        return
    fig = px.treemap(df, path=path, values=values, title=title, color_discrete_sequence=COLORS)
    fig.update_layout(template=CHART_THEME, paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
    st.plotly_chart(fig, use_container_width=True)


def gantt_chart(data: list, title: str = "Project Timeline"):
    if not data:
        st.info("No project timeline data.")
        return
    df = pd.DataFrame(data)
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Status", title=title, color_discrete_sequence=COLORS)
    fig.update_layout(template=CHART_THEME, paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)


def heatmap_chart(df: pd.DataFrame, title: str = "Workload Heatmap"):
    if df.empty:
        st.info("No workload data.")
        return
    fig = px.imshow(df, title=title, color_continuous_scale=[[0, "#1E293B"], [0.5, "#6366F1"], [1, "#06B6D4"]], aspect="auto")
    fig.update_layout(template=CHART_THEME, paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
    st.plotly_chart(fig, use_container_width=True)


def leaderboard_chart(df: pd.DataFrame, title: str = "Employee Ranking"):
    if df.empty:
        st.info("No ranking data.")
        return
    fig = px.bar(df, x="Hours", y="Employee", orientation="h", title=title, color="Hours", color_continuous_scale=[[0, COLORS[0]], [1, COLORS[2]]])
    fig.update_layout(template=CHART_THEME, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
