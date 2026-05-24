from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)
from intpy.domain.models import Task, TaskPriority, TaskStatus


class TaskDialog(QDialog):
    def __init__(self, task: Task | None = None, default_status: str | None = None, parent=None) -> None:
        super().__init__(parent)
        self.task = task
        self.default_status = default_status
        self.is_edit_mode = task is not None

        self.setWindowTitle("Edit Task" if self.is_edit_mode else "New Task")
        self.resize(400, 320)
        self.setModal(True)

        self._setup_ui()
        if self.is_edit_mode:
            self._populate_fields()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header Title
        header = QLabel("Edit Task" if self.is_edit_mode else "Create Task", self)
        header.setObjectName("titleLabel")
        main_layout.addWidget(header)

        # Form Layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # 1. Title Input
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Enter task title (required)")
        form_layout.addRow(QLabel("Title:"), self.title_input)

        # 2. Description Input
        self.desc_input = QTextEdit(self)
        self.desc_input.setPlaceholderText("Enter optional description")
        self.desc_input.setMaximumHeight(80)
        form_layout.addRow(QLabel("Description:"), self.desc_input)

        # 3. Priority Selection
        self.prio_combo = QComboBox(self)
        for prio in TaskPriority:
            self.prio_combo.addItem(prio.value, prio)
        self.prio_combo.setCurrentIndex(1)  # Default: MEDIUM
        form_layout.addRow(QLabel("Priority:"), self.prio_combo)

        # 4. Status Selection (Visible only in edit mode)
        if self.is_edit_mode:
            self.status_combo = QComboBox(self)
            for status in TaskStatus:
                self.status_combo.addItem(status.value, status)
            form_layout.addRow(QLabel("Status:"), self.status_combo)

        main_layout.addLayout(form_layout)

        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save" if self.is_edit_mode else "Create", self)
        self.save_btn.setObjectName("addBtn")
        self.save_btn.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(self.save_btn)

        main_layout.addLayout(btn_layout)

    def _populate_fields(self) -> None:
        """Populates form fields with existing Task details during Edit mode."""
        assert self.task is not None
        self.title_input.setText(self.task.title)
        self.desc_input.setPlainText(self.task.description)
        
        # Select current priority
        prio_idx = self.prio_combo.findData(self.task.priority)
        if prio_idx != -1:
            self.prio_combo.setCurrentIndex(prio_idx)
            
        # Select current status
        status_idx = self.status_combo.findData(self.task.status)
        if status_idx != -1:
            self.status_combo.setCurrentIndex(status_idx)

    def _validate_and_accept(self) -> None:
        """Performs form-level client-side input validations before accepting."""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Task title cannot be empty.",
                QMessageBox.Ok
            )
            return

        if len(title) > 100:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Task title cannot exceed 100 characters.",
                QMessageBox.Ok
            )
            return

        desc = self.desc_input.toPlainText().strip()
        if len(desc) > 500:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Task description cannot exceed 500 characters.",
                QMessageBox.Ok
            )
            return

        self.accept()

    # =========================================================================
    # Data Accessors
    # =========================================================================

    def get_title(self) -> str:
        return self.title_input.text().strip()

    def get_description(self) -> str:
        return self.desc_input.toPlainText().strip()

    def get_priority(self) -> TaskPriority:
        return self.prio_combo.currentData()

    def get_status(self) -> TaskStatus:
        if self.is_edit_mode:
            return self.status_combo.currentData()
        elif self.default_status is not None:
            return TaskStatus(self.default_status)
        return TaskStatus.TODO
