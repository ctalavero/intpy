"""
PrinterService — generates a PDF report of all tasks with a QR code.

Uses: fpdf2, qrcode, pandas.
"""
import io
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import qrcode
from fpdf import FPDF

from intpy.domain.models import Task, TaskPriority, TaskStatus
from intpy.service.task_service import TaskService


class _ReportPDF(FPDF):
    """Custom FPDF subclass with header/footer branding."""

    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(40, 40, 60)
        self.cell(0, 12, "TaskHub", align="L")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(130, 130, 150)
        self.cell(0, 12, datetime.now().strftime("Generated: %Y-%m-%d %H:%M"), align="R")
        self.ln(16)
        # Separator line
        self.set_draw_color(70, 111, 165)
        self.set_line_width(0.6)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


# ---------------------------------------------------------------------------
# Status / Priority visual helpers
# ---------------------------------------------------------------------------
_STATUS_COLORS = {
    TaskStatus.TODO: (180, 180, 190),
    TaskStatus.IN_PROGRESS: (230, 180, 50),
    TaskStatus.DONE: (80, 190, 80),
}

_PRIORITY_COLORS = {
    TaskPriority.LOW: (100, 160, 230),
    TaskPriority.MEDIUM: (230, 180, 50),
    TaskPriority.HIGH: (220, 70, 70),
}


class PrinterService:
    """Service that generates a PDF report from TaskService data."""

    def __init__(self, task_service: TaskService) -> None:
        self.task_service = task_service

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_pdf(self, output_path: str | Path = "tasks_report.pdf") -> str:
        """
        Generate a styled PDF report with a task table and QR code.

        Returns the absolute path to the saved PDF file.
        """
        output_path = Path(output_path).resolve()
        tasks = self.task_service.list_tasks()

        pdf = _ReportPDF()
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(40, 40, 60)
        pdf.cell(0, 14, "Task Report", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # Subtitle
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(100, 100, 120)
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        todo = sum(1 for t in tasks if t.status == TaskStatus.TODO)
        pdf.cell(
            0, 8,
            f"Total tasks: {total}  |  TODO: {todo}  |  In Progress: {in_progress}  |  Done: {done}",
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
        pdf.ln(8)

        # Task table
        if tasks:
            self._draw_task_table(pdf, tasks)
        else:
            pdf.set_font("Helvetica", "I", 12)
            pdf.set_text_color(160, 160, 160)
            pdf.cell(0, 10, "No tasks found.", align="C", new_x="LMARGIN", new_y="NEXT")

        # QR code
        pdf.ln(10)
        self._draw_qr_code(pdf, tasks)

        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(output_path))
        return str(output_path)

    def generate_pdf_bytes(self) -> bytes:
        """Generate PDF and return raw bytes (useful for Streamlit downloads)."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
            self.generate_pdf(tmp.name)
            return Path(tmp.name).read_bytes()

    def get_tasks_dataframe(self) -> pd.DataFrame:
        """Return all tasks as a pandas DataFrame."""
        tasks = self.task_service.list_tasks()
        return self._tasks_to_dataframe(tasks)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tasks_to_dataframe(tasks: list[Task]) -> pd.DataFrame:
        if not tasks:
            return pd.DataFrame(columns=["ID", "Title", "Description", "Priority", "Status", "Created"])
        rows = []
        for t in tasks:
            rows.append({
                "ID": t.id,
                "Title": t.title,
                "Description": t.description or "—",
                "Priority": t.priority.value,
                "Status": t.status.value,
                "Created": t.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        return pd.DataFrame(rows)

    def _draw_task_table(self, pdf: _ReportPDF, tasks: list[Task]) -> None:
        col_widths = [12, 50, 55, 22, 28, 28]  # ID, Title, Desc, Prio, Status, Created
        headers = ["ID", "Title", "Description", "Priority", "Status", "Created"]

        # Header row
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(50, 55, 75)
        pdf.set_text_color(255, 255, 255)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 9, header, border=1, fill=True, align="C")
        pdf.ln()

        # Data rows
        pdf.set_font("Helvetica", "", 9)
        for idx, task in enumerate(tasks):
            # Alternate row color
            if idx % 2 == 0:
                pdf.set_fill_color(245, 245, 250)
            else:
                pdf.set_fill_color(255, 255, 255)

            fill = True
            pdf.set_text_color(40, 40, 60)

            row_data = [
                str(task.id),
                self._truncate(task.title, 28),
                self._truncate(task.description or "—", 30),
            ]

            for i, text in enumerate(row_data):
                pdf.cell(col_widths[i], 8, text, border=1, fill=fill, align="L" if i > 0 else "C")

            # Priority with color
            prio_color = _PRIORITY_COLORS.get(task.priority, (100, 100, 100))
            pdf.set_text_color(*prio_color)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(col_widths[3], 8, task.priority.value, border=1, fill=fill, align="C")

            # Status with color
            status_color = _STATUS_COLORS.get(task.status, (100, 100, 100))
            pdf.set_text_color(*status_color)
            pdf.cell(col_widths[4], 8, task.status.value, border=1, fill=fill, align="C")

            # Date
            pdf.set_text_color(100, 100, 120)
            pdf.set_font("Helvetica", "", 9)
            created_str = task.created_at.strftime("%Y-%m-%d")
            pdf.cell(col_widths[5], 8, created_str, border=1, fill=fill, align="C")

            pdf.ln()

    def _draw_qr_code(self, pdf: _ReportPDF, tasks: list[Task]) -> None:
        # Generate QR content
        qr_text = (
            f"TaskHub Report | {len(tasks)} tasks | "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save QR to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp, format="PNG")
            tmp_path = tmp.name

        try:
            # Center the QR on the page
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(40, 40, 60)
            pdf.cell(0, 10, "QR Code", align="C", new_x="LMARGIN", new_y="NEXT")

            qr_size = 40
            x_center = (pdf.w - qr_size) / 2
            pdf.image(tmp_path, x=x_center, w=qr_size)

            pdf.ln(qr_size + 4)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(140, 140, 160)
            pdf.cell(0, 6, qr_text, align="C", new_x="LMARGIN", new_y="NEXT")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @staticmethod
    def _truncate(text: str, max_len: int) -> str:
        if len(text) <= max_len:
            return text
        return text[: max_len - 2] + ".."
