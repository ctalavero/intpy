from PySide6.QtCore import QMimeData, QPoint, Qt, Signal
from PySide6.QtGui import QAction, QColor, QDrag, QFont, QMouseEvent
from PySide6.QtWidgets import QApplication, QFrame, QGraphicsDropShadowEffect, QLabel, QMenu, QVBoxLayout
from intpy.domain.models import Task, TaskPriority
from intpy.gui.style import CARD_STYLE_HIGH, CARD_STYLE_LOW, CARD_STYLE_MEDIUM


class TaskCard(QFrame):
    double_clicked = Signal(int)  # Emits Task ID
    task_deleted = Signal(int)     # Emits Task ID
    task_updated = Signal(int)     # Emits Task ID

    def __init__(self, task: Task, parent=None) -> None:
        super().__init__(parent)
        self.task = task
        self.drag_start_position = QPoint()

        self.setObjectName("taskCard")
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        # Title Label (Bold)
        self.title_label = QLabel(self.task.title, self)
        font = QFont("Inter", 11, QFont.Bold)
        self.title_label.setFont(font)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("color: #ffffff; border: none; background: transparent;")
        layout.addWidget(self.title_label)

        # Description Label (Muted text, smaller, wrapped)
        desc_text = self.task.description.strip() if self.task.description else "---"
        self.desc_label = QLabel(desc_text, self)
        self.desc_label.setFont(QFont("Inter", 9))
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #a0a0b2; border: none; background: transparent;")
        layout.addWidget(self.desc_label)

        # Bottom info (Priority tag & created date)
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(2)

        prio_text = f"Priority: {self.task.priority.value}"
        self.prio_label = QLabel(prio_text, self)
        self.prio_label.setFont(QFont("Inter", 8, QFont.Bold))
        # Color specific priority sub-tags
        if self.task.priority == TaskPriority.HIGH:
            self.prio_label.setStyleSheet("color: #ff5555; border: none; background: transparent;")
        elif self.task.priority == TaskPriority.MEDIUM:
            self.prio_label.setStyleSheet("color: #ffb86c; border: none; background: transparent;")
        else:
            self.prio_label.setStyleSheet("color: #8be9fd; border: none; background: transparent;")
        bottom_layout.addWidget(self.prio_label)

        date_text = self.task.created_at.strftime("%Y-%m-%d %H:%M")
        self.date_label = QLabel(date_text, self)
        self.date_label.setFont(QFont("Inter", 8))
        self.date_label.setStyleSheet("color: #6272a4; border: none; background: transparent;")
        bottom_layout.addWidget(self.date_label)

        layout.addLayout(bottom_layout)

        # Apply realistic sticky note drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        # Set fixed size elements to give a "square-ish" sticky note look
        self.setMinimumHeight(130)
        self.setMaximumHeight(180)
        self.setMinimumWidth(160)

    def _apply_style(self) -> None:
        """Applies style sheets representing the task's priority."""
        if self.task.priority == TaskPriority.HIGH:
            self.setStyleSheet(CARD_STYLE_HIGH)
        elif self.task.priority == TaskPriority.MEDIUM:
            self.setStyleSheet(CARD_STYLE_MEDIUM)
        else:
            self.setStyleSheet(CARD_STYLE_LOW)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Captures mouse press position to check for drag threshold."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Initiates a Drag operation carrying the task ID if drag threshold is crossed."""
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.task.id))
        drag.setMimeData(mime_data)

        # Visual drag pixmap (simple snapshot of the card)
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        # Start Drag
        drag.exec(Qt.MoveAction)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Triggers double-clicked edit dialog signal."""
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.task.id)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event) -> None:
        """Shows right-click options for rapid editing and deleting."""
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #1a1a20; color: white; border: 1px solid #32323f; border-radius: 6px; } QMenu::item:selected { background-color: #32323f; }")

        edit_action = QAction("✏️ Edit Task", self)
        edit_action.triggered.connect(lambda: self.double_clicked.emit(self.task.id))
        menu.addAction(edit_action)

        delete_action = QAction("🗑️ Delete Task", self)
        delete_action.triggered.connect(lambda: self.task_deleted.emit(self.task.id))
        menu.addAction(delete_action)

        menu.exec(event.globalPos())
