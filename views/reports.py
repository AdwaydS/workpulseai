"""Reports generation page."""

from datetime import date, timedelta

import streamlit as st

from components.theme import render_header
from utils.session import get_db_session, has_role
from services.attendance_service import AttendanceService
from services.worklog_service import WorkLogService
from services.project_service import ProjectService
from services.user_service import UserService
from reports.report_service import ReportService


def render():
    render_header()
    user = st.session_state.user
    db = get_db_session()

    try:
        att_svc = AttendanceService(db)
        wl_svc = WorkLogService(db)
        proj_svc = ProjectService(db)
        user_svc = UserService(db)
        report_svc = ReportService()

        st.markdown("### 📄 Report Generator")

        c1, c2, c3 = st.columns(3)
        with c1:
            report_type = st.selectbox("Report Type", [
                "Attendance", "Work Logs", "Projects", "Employees", "Productivity"
            ])
        with c2:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        with c3:
            end_date = st.date_input("End Date", value=date.today())

        format_type = st.radio("Export Format", ["Excel", "CSV", "PDF"], horizontal=True)

        if st.button("Generate Report", use_container_width=True):
            if report_type == "Attendance":
                data = att_svc.get_attendance_report_data(start_date, end_date)
            elif report_type == "Work Logs":
                data = wl_svc.to_dataframe_rows(user["id"] if not has_role("admin", "manager") else None)
            elif report_type == "Projects":
                data = proj_svc.to_dataframe_rows()
            elif report_type == "Employees":
                if not has_role("admin"):
                    st.error("Admin access required for employee reports.")
                    return
                data = user_svc.to_dataframe_rows()
            else:
                data = wl_svc.to_dataframe_rows()

            if not data:
                st.warning("No data found for the selected criteria.")
                return

            filename = f"{report_type.lower().replace(' ', '_')}_{start_date}_{end_date}"

            if format_type == "Excel":
                content = report_svc.generate_excel(data, filename)
                st.download_button("Download Excel", content, f"{filename}.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            elif format_type == "CSV":
                content = report_svc.generate_csv(data)
                st.download_button("Download CSV", content, f"{filename}.csv", "text/csv")
            else:
                content = report_svc.generate_pdf(f"{report_type} Report", data, subtitle=f"{start_date} to {end_date}")
                st.download_button("Download PDF", content, f"{filename}.pdf", "application/pdf")

            st.success(f"{report_type} report generated with {len(data)} records.")

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Multi-Sheet Export (Admin)")
        if has_role("admin") and st.button("Export All Data (Excel)"):
            from services.excel_service import ExcelService
            multi = {
                "Employees": user_svc.to_dataframe_rows(),
                "Projects": proj_svc.to_dataframe_rows(),
                "Attendance": att_svc.get_attendance_report_data(start_date, end_date),
                "Work Logs": wl_svc.to_dataframe_rows(),
            }
            content = ExcelService.export_multi_sheet(multi)
            st.download_button("Download Full Export", content, "workpulse_full_export.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()
