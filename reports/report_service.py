"""Report generation service - PDF, Excel, CSV."""

import io
import os
from datetime import date, datetime
from typing import List, Dict, Optional

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

from services.excel_service import ExcelService


class ReportService:
    REPORTS_DIR = "reports/output"

    def __init__(self):
        os.makedirs(self.REPORTS_DIR, exist_ok=True)

    def generate_excel(self, data: List[Dict], filename: str, sheet_name: str = "Report") -> bytes:
        df = pd.DataFrame(data)
        return ExcelService.dataframe_to_excel(df, sheet_name)

    def generate_csv(self, data: List[Dict]) -> str:
        return ExcelService.dataframe_to_csv(pd.DataFrame(data))

    def generate_pdf(
        self,
        title: str,
        data: List[Dict],
        logo_path: str = "assets/logo.png",
        subtitle: str = "",
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=0.5 * inch)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=18, spaceAfter=12, textColor=colors.HexColor("#6366F1"))
        elements = []

        if os.path.exists(logo_path):
            try:
                elements.append(Image(logo_path, width=1.2 * inch, height=1.2 * inch))
            except Exception:
                pass

        elements.append(Paragraph(title, title_style))
        if subtitle:
            elements.append(Paragraph(subtitle, styles["Normal"]))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))

        if data:
            headers = list(data[0].keys())
            table_data = [headers] + [[str(row.get(h, "")) for h in headers] for row in data[:500]]
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366F1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            elements.append(table)

        doc.build(elements)
        return buffer.getvalue()

    def save_report(self, content: bytes, filename: str) -> str:
        path = os.path.join(self.REPORTS_DIR, filename)
        with open(path, "wb") as f:
            f.write(content)
        return path
