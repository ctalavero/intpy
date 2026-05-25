"""
TaskHub — Streamlit Web Application.

Run with:
    uv run streamlit run intpy/web/web_app.py
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ensure project root is importable
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from intpy.repository.json_repo import JsonTaskRepository
from intpy.service.printer_service import PrinterService
from intpy.service.task_service import TaskService
from intpy.domain.models import TaskStatus, TaskPriority

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TaskHub",
    page_icon="📋",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Bootstrap services
# ---------------------------------------------------------------------------
DB_PATH = "tasks.json"


@st.cache_resource
def get_service():
    repo = JsonTaskRepository(DB_PATH)
    return TaskService(repo)


def get_printer():
    return PrinterService(get_service())


# ---------------------------------------------------------------------------
# Sidebar — task management
# ---------------------------------------------------------------------------
st.sidebar.title("📋 TaskHub")
st.sidebar.markdown("---")

# Add Task form
st.sidebar.subheader("➕ Add Task")
with st.sidebar.form("add_task_form", clear_on_submit=True):
    new_title = st.text_input("Title", placeholder="Enter task title...")
    new_desc = st.text_area("Description", placeholder="Optional description...", height=80)
    new_priority = st.selectbox("Priority", ["MEDIUM", "LOW", "HIGH"])
    submitted = st.form_submit_button("Add Task", use_container_width=True)
    if submitted:
        if new_title.strip():
            try:
                service = get_service()
                task = service.create_task(
                    title=new_title.strip(),
                    description=new_desc.strip(),
                    priority=new_priority,
                )
                st.sidebar.success(f"✔ Task #{task.id} created!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"✖ Error: {e}")
        else:
            st.sidebar.warning("Title cannot be empty.")

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.title("📋 TaskHub — Task Dashboard")
st.markdown("---")

service = get_service()
all_tasks = service.list_tasks()

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", len(all_tasks))
col2.metric("TODO", sum(1 for t in all_tasks if t.status == TaskStatus.TODO))
col3.metric("In Progress", sum(1 for t in all_tasks if t.status == TaskStatus.IN_PROGRESS))
col4.metric("Done", sum(1 for t in all_tasks if t.status == TaskStatus.DONE))

st.markdown("---")

# Task table
if all_tasks:
    printer = get_printer()
    df = printer.get_tasks_dataframe()
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Priority": st.column_config.TextColumn("Priority", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
        },
    )
else:
    st.info("No tasks found. Add a task using the sidebar form.")

st.markdown("---")

# ---------------------------------------------------------------------------
# PDF Export section
# ---------------------------------------------------------------------------
st.subheader("📄 PDF Report")

pdf_col1, pdf_col2 = st.columns([1, 3])

with pdf_col1:
    if st.button("🖨️ Generate PDF", use_container_width=True, type="primary"):
        try:
            printer = get_printer()
            pdf_bytes = printer.generate_pdf_bytes()
            st.session_state["pdf_bytes"] = pdf_bytes
            st.session_state["pdf_ready"] = True
            st.success("✔ PDF generated!")
        except Exception as e:
            st.error(f"✖ Error: {e}")

with pdf_col2:
    if st.session_state.get("pdf_ready"):
        st.download_button(
            label="⬇️ Download PDF",
            data=st.session_state["pdf_bytes"],
            file_name="tasks_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# ---------------------------------------------------------------------------
# QR Code preview
# ---------------------------------------------------------------------------
if st.session_state.get("pdf_ready") and all_tasks:
    import qrcode
    import io
    from datetime import datetime

    st.markdown("---")
    st.subheader("📱 QR Code")

    qr_text = f"TaskHub Report | {len(all_tasks)} tasks | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption=qr_text, width=250)

# ---------------------------------------------------------------------------
# Task actions (edit / delete)
# ---------------------------------------------------------------------------
if all_tasks:
    st.markdown("---")
    st.subheader("✏️ Quick Actions")

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        task_ids = [t.id for t in all_tasks]
        selected_id = st.selectbox("Select task ID", task_ids)
        new_status = st.selectbox(
            "Change status to",
            [s.value for s in TaskStatus],
        )
        if st.button("Update Status", use_container_width=True):
            try:
                service.update_task(selected_id, status=new_status)
                st.success(f"✔ Task #{selected_id} → {new_status}")
                st.rerun()
            except Exception as e:
                st.error(f"✖ Error: {e}")

    with action_col2:
        del_id = st.selectbox("Delete task ID", task_ids, key="del_id")
        st.text("")  # spacer
        st.text("")  # spacer
        if st.button("🗑️ Delete Task", use_container_width=True):
            try:
                service.delete_task(del_id)
                st.success(f"✔ Task #{del_id} deleted!")
                st.rerun()
            except Exception as e:
                st.error(f"✖ Error: {e}")
