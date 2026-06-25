"""Data table components with Excel import/export."""

import io
from typing import List, Dict, Callable, Optional

import pandas as pd
import streamlit as st

from services.excel_service import ExcelService


def render_data_table(
    data: List[Dict],
    title: str = "Data",
    key: str = "table",
    editable: bool = False,
    show_export: bool = True,
    show_import: bool = False,
    import_handler: Optional[Callable] = None,
    template_type: Optional[str] = None,
):
    if not data:
        st.info(f"No {title.lower()} records found.")
        return None

    df = pd.DataFrame(data)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"### {title}")
    with col2:
        if show_export:
            export_format = st.selectbox("Export", ["Excel", "CSV"], key=f"{key}_export_fmt", label_visibility="collapsed")
    with col3:
        if show_export:
            if export_format == "Excel":
                excel_bytes = ExcelService.dataframe_to_excel(df, title)
                st.download_button("📥 Download", excel_bytes, f"{key}_{title.lower().replace(' ', '_')}.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"{key}_dl")
            else:
                st.download_button("📥 Download", ExcelService.dataframe_to_csv(df), f"{key}_{title.lower().replace(' ', '_')}.csv",
                                   "text/csv", key=f"{key}_dl_csv")

    if show_import:
        st.markdown("#### Import Data")
        icol1, icol2 = st.columns(2)
        with icol1:
            uploaded = st.file_uploader("Upload Excel/CSV", type=["xlsx", "xls", "csv"], key=f"{key}_upload")
        with icol2:
            if template_type:
                template = ExcelService.get_template(template_type)
                st.download_button("📋 Download Template", template, f"{template_type}_template.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"{key}_template")

        if uploaded and import_handler:
            if uploaded.name.endswith(".csv"):
                import_df, err = ExcelService.read_csv(uploaded)
            else:
                import_df, err = ExcelService.read_excel(uploaded)
            if err:
                st.error(f"Import error: {err}")
            else:
                st.dataframe(import_df.head(10), use_container_width=True)
                if st.button("Confirm Import", key=f"{key}_import_btn"):
                    rows = ExcelService.rows_from_dataframe(import_df)
                    count = import_handler(rows)
                    st.success(f"Successfully imported {count} records.")
                    st.rerun()

    search = st.text_input("🔍 Search", key=f"{key}_search", placeholder="Filter records...")
    display_df = df
    if search:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]

    if editable:
        edited = st.data_editor(display_df, use_container_width=True, num_rows="dynamic", key=f"{key}_editor")
        return edited
    else:
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        return display_df


def render_html_table(data: List[Dict], max_rows: int = 50):
    if not data:
        return
    headers = list(data[0].keys())
    rows_html = ""
    for row in data[:max_rows]:
        cells = "".join(f"<td>{row.get(h, '')}</td>" for h in headers)
        rows_html += f"<tr>{cells}</tr>"
    headers_html = "".join(f"<th>{h}</th>" for h in headers)
    st.markdown(f"""
    <table class="data-table">
        <thead><tr>{headers_html}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
