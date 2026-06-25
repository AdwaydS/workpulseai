"""Excel and CSV import/export service."""

import io
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import pandas as pd


class ExcelService:
    """Handles Excel/CSV import and export for all modules."""

    @staticmethod
    def dataframe_to_excel(df: pd.DataFrame, sheet_name: str = "Data") -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            ws = writer.sheets[sheet_name]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
        return output.getvalue()

    @staticmethod
    def dataframe_to_csv(df: pd.DataFrame) -> str:
        return df.to_csv(index=False)

    @staticmethod
    def read_excel(uploaded_file) -> Tuple[pd.DataFrame, Optional[str]]:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            return df, None
        except Exception as e:
            return pd.DataFrame(), str(e)

    @staticmethod
    def read_csv(uploaded_file) -> Tuple[pd.DataFrame, Optional[str]]:
        try:
            df = pd.read_csv(uploaded_file)
            return df, None
        except Exception as e:
            return pd.DataFrame(), str(e)

    @staticmethod
    def rows_from_dataframe(df: pd.DataFrame) -> List[Dict]:
        df = df.fillna("")
        return df.to_dict(orient="records")

    @staticmethod
    def export_multi_sheet(data: Dict[str, List[Dict]], filename_prefix: str = "report") -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for sheet_name, rows in data.items():
                df = pd.DataFrame(rows)
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        return output.getvalue()

    @staticmethod
    def get_template(template_type: str) -> bytes:
        templates = {
            "users": ["Employee ID", "Email", "Username", "First Name", "Last Name", "Role", "Department", "Job Title", "Password"],
            "projects": ["Project Name", "Client", "Budget", "Status", "Progress %", "Allocated Hours", "Consumed Hours"],
            "work_logs": ["Date", "Project", "Task", "Description", "Priority", "Hours", "Completion %", "Notes"],
            "attendance": ["Employee ID", "Name", "Date", "Login", "Logout", "Status", "Working Hours", "Overtime"],
        }
        cols = templates.get(template_type, ["Column1", "Column2"])
        df = pd.DataFrame(columns=cols)
        return ExcelService.dataframe_to_excel(df, "Template")
