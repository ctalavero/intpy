from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from intpy.domain.models import TaskStatus
from intpy.repository.json_repo import JsonTaskRepository
from intpy.service.printer_service import PrinterService
from intpy.service.task_service import TaskService
from intpy.gui.column import KanbanColumn
from intpy.gui.dialogs import TaskDialog



class MainWindow(QMainWindow):
    def __init__(self, db_path: str = "tasks.json") -> None:
        super().__init__()
        self.setWindowTitle("TaskHub Kanban Board")
        self.resize(1100, 700)

        # Bootstrap SOLID Backend
        repo = JsonTaskRepository(db_path)
        self.service = TaskService(repo)

        self._setup_ui()
        self.load_tasks()

    def _setup_ui(self) -> None:
        # Main central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # -------------------------------------------------------------
        # Header Toolbar Layout
        # -------------------------------------------------------------
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(15)

        # App Title
        title_label = QLabel("TaskHub Board 📋", self)
        title_label.setFont(QFont("Inter", 18, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        toolbar_layout.addWidget(title_label)

        toolbar_layout.addStretch()

        # Dynamic Search Bar (Premium Filter effect)
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("🔍 Search tasks...")
        self.search_input.setFixedWidth(240)
        self.search_input.textChanged.connect(self.load_tasks)
        toolbar_layout.addWidget(self.search_input)

        # Add Task Button (Global)
        global_add_btn = QPushButton("＋ Add Task", self)
        global_add_btn.setObjectName("addBtn")
        global_add_btn.clicked.connect(lambda: self.handle_add_task(TaskStatus.TODO.value))
        toolbar_layout.addWidget(global_add_btn)

        # Export PDF Button
        pdf_btn = QPushButton("📄 Export PDF", self)
        pdf_btn.setObjectName("addBtn")
        pdf_btn.clicked.connect(self.handle_export_pdf)
        toolbar_layout.addWidget(pdf_btn)

        # Clear All Button
        clear_btn = QPushButton("🗑️ Clear All", self)
        clear_btn.setObjectName("deleteBtn")
        clear_btn.clicked.connect(self.handle_clear_board)
        toolbar_layout.addWidget(clear_btn)

        main_layout.addLayout(toolbar_layout)

        # -------------------------------------------------------------
        # Kanban Columns Layout (3 Column layout)
        # -------------------------------------------------------------
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(16)

        # 1. TODO Column
        self.todo_col = KanbanColumn("To Do", TaskStatus.TODO, self)
        self.todo_col.task_dropped.connect(self.handle_task_dropped)
        self.todo_col.add_clicked.connect(self.handle_add_task)
        self.todo_col.edit_requested.connect(self.handle_edit_task)
        self.todo_col.delete_requested.connect(self.handle_delete_task)
        columns_layout.addWidget(self.todo_col)

        # 2. IN PROGRESS Column
        self.progress_col = KanbanColumn("In Progress", TaskStatus.IN_PROGRESS, self)
        self.progress_col.task_dropped.connect(self.handle_task_dropped)
        self.progress_col.add_clicked.connect(self.handle_add_task)
        self.progress_col.edit_requested.connect(self.handle_edit_task)
        self.progress_col.delete_requested.connect(self.handle_delete_task)
        columns_layout.addWidget(self.progress_col)

        # 3. DONE Column
        self.done_col = KanbanColumn("Done", TaskStatus.DONE, self)
        self.done_col.task_dropped.connect(self.handle_task_dropped)
        self.done_col.add_clicked.connect(self.handle_add_task)
        self.done_col.edit_requested.connect(self.handle_edit_task)
        self.done_col.delete_requested.connect(self.handle_delete_task)
        columns_layout.addWidget(self.done_col)

        main_layout.addLayout(columns_layout)

    def load_tasks(self) -> None:
        """Loads and splits tasks into their respective columns, applying search filter."""
        search_query = self.search_input.text().strip().lower()

        # Fetch all tasks from service
        all_tasks = self.service.list_tasks()

        # Filter by search string (title or description match)
        if search_query:
            all_tasks = [
                t for t in all_tasks
                if search_query in t.title.lower() or search_query in t.description.lower()
            ]

        # Categorize
        todo_tasks = [t for t in all_tasks if t.status == TaskStatus.TODO]
        progress_tasks = [t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]
        done_tasks = [t for t in all_tasks if t.status == TaskStatus.DONE]

        # Populate GUI columns
        self.todo_col.populate_tasks(todo_tasks)
        self.progress_col.populate_tasks(progress_tasks)
        self.done_col.populate_tasks(done_tasks)

    # =========================================================================
    # Event Handlers
    # =========================================================================

    def handle_task_dropped(self, task_id: int, target_status: str) -> None:
        """Handles updating task status when dragged & dropped between columns."""
        try:
            self.service.update_task(task_id, status=target_status)
            self.load_tasks()
        except Exception as e:
            QMessageBox.critical(self, "System Error", f"Failed to move task: {e}")

    def handle_add_task(self, default_status: str) -> None:
        """Opens dialog to create a new task inside a default status."""
        dialog = TaskDialog(default_status=default_status, parent=self)
        if dialog.exec() == TaskDialog.Accepted:
            try:
                # 1. Create task
                task = self.service.create_task(
                    title=dialog.get_title(),
                    description=dialog.get_description(),
                    priority=dialog.get_priority(),
                )
                # 2. If column added to is not TODO, update status
                if default_status != TaskStatus.TODO.value:
                    self.service.update_task(task.id, status=default_status)

                self.load_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create task: {e}")

    def handle_edit_task(self, task_id: int) -> None:
        """Opens edit dialog for a specific task."""
        try:
            task = self.service.get_task(task_id)
            dialog = TaskDialog(task=task, parent=self)
            if dialog.exec() == TaskDialog.Accepted:
                self.service.update_task(
                    task_id=task_id,
                    title=dialog.get_title(),
                    description=dialog.get_description(),
                    status=dialog.get_status(),
                    priority=dialog.get_priority(),
                )
                self.load_tasks()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit task: {e}")

    def handle_delete_task(self, task_id: int) -> None:
        """Deletes a task by ID after confirmation request."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this task?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.delete_task(task_id)
                self.load_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete task: {e}")

    def handle_clear_board(self) -> None:
        """Deletes all tasks after explicit user confirmation."""
        tasks = self.service.list_tasks()
        if not tasks:
            QMessageBox.information(self, "Board Clear", "The board is already empty.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Clear Board",
            "Are you sure you want to delete ALL tasks permanently?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                for task in tasks:
                    self.service.delete_task(task.id)
                self.load_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear board: {e}")

    def handle_export_pdf(self) -> None:
        """Generates a PDF report and saves it via a file dialog."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            "tasks_report.pdf",
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return  # User cancelled

        try:
            printer = PrinterService(self.service)
            saved_path = printer.generate_pdf(file_path)
            QMessageBox.information(
                self, "PDF Exported",
                f"Report saved successfully!\n\n{saved_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to generate PDF:\n{e}")
