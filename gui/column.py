from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from intpy.domain.models import Task, TaskStatus
from intpy.gui.card import TaskCard


class KanbanColumn(QFrame):
    # Emits task ID and the column's target status when a drop occurs
    task_dropped = Signal(int, str)
    add_clicked = Signal(str)        # Emits column status
    edit_requested = Signal(int)     # Emits task ID
    delete_requested = Signal(int)   # Emits task ID

    def __init__(self, title: str, status: TaskStatus, parent=None) -> None:
        super().__init__(parent)
        self.title = title
        self.status = status

        self.setObjectName("kanbanColumn")
        self.setAcceptDrops(True)

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header panel
        header_widget = QWidget(self)
        header_widget.setObjectName("kanbanColumnHeader")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 5, 5, 5)

        # Status Title Label with Counter
        self.title_label = QLabel(self.title, header_widget)
        self.title_label.setObjectName("columnTitle")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # "+" Add button
        self.add_btn = QPushButton("＋", header_widget)
        self.add_btn.setFixedSize(28, 28)
        self.add_btn.setFont(QFont("Inter", 12, QFont.Bold))
        self.add_btn.setStyleSheet(
            "QPushButton { background-color: #2b2b36; border-radius: 6px; padding: 0px; color: #a0a0b2; }"
            "QPushButton:hover { background-color: #44475a; color: white; }"
        )
        self.add_btn.clicked.connect(lambda: self.add_clicked.emit(self.status.value))
        header_layout.addWidget(self.add_btn)

        main_layout.addWidget(header_widget)

        # Scroll Area for Task Cards
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Scroll Content Container Widget
        self.content_widget = QWidget(self.scroll_area)
        self.content_widget.setObjectName("scrollContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(12)
        self.content_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

    def clear_cards(self) -> None:
        """Clears all card widgets from the column layout."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def populate_tasks(self, tasks: list[Task]) -> None:
        """Clears the column and populates it with a new list of tasks."""
        self.clear_cards()

        # Update counter in title
        self.title_label.setText(f"{self.title} ({len(tasks)})")

        for task in tasks:
            card = TaskCard(task, self)
            card.double_clicked.connect(self.edit_requested.emit)
            card.task_deleted.connect(self.delete_requested.emit)
            self.content_layout.addWidget(card)

    # =========================================================================
    # Drag and Drop events
    # =========================================================================

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Accepts a drag if it contains task ID text."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        """Requires accepting moving layout drops."""
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Extracts the Task ID from the drag object and triggers drop signal."""
        task_id_str = event.mimeData().text()
        try:
            task_id = int(task_id_str)
            self.task_dropped.emit(task_id, self.status.value)
            event.acceptProposedAction()
        except ValueError:
            pass
        super().dropEvent(event)
