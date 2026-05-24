# Premium Dark Glassmorphic QSS Stylesheet for TaskHub GUI

# Color definitions
BG_COLOR = "#0f0f11"          # Ultra dark charcoal background
CARD_BG_DEFAULT = "#1d1d22"   # Card background for tasks
PANEL_BG = "#16161b"          # Kanban column background
TEXT_MAIN = "#f8f8f2"         # White main text
TEXT_MUTED = "#8f8f9e"        # Muted gray text

BORDER_RADIUS_PANEL = "12px"
BORDER_RADIUS_CARD = "10px"

QSS_STYLESHEET = """
QMainWindow {
    background-color: %s;
}

QDialog {
    background-color: %s;
    border: 1px solid #2d2d37;
    border-radius: 12px;
}

QLabel {
    color: %s;
    font-size: 13px;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}

QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
    padding-bottom: 10px;
}

QLineEdit, QTextEdit {
    background-color: #1a1a20;
    color: #ffffff;
    border: 1px solid #32323f;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    selection-background-color: #4b4b5e;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #6272a4;
    background-color: #202028;
}

QComboBox {
    background-color: #1a1a20;
    color: #ffffff;
    border: 1px solid #32323f;
    border-radius: 6px;
    padding: 6px;
    font-size: 13px;
    min-width: 100px;
}

QComboBox:on {
    border: 1px solid #6272a4;
}

QComboBox QAbstractItemView {
    background-color: #1a1a20;
    color: #ffffff;
    selection-background-color: #32323f;
    border: 1px solid #32323f;
}

QPushButton {
    background-color: #2b2b36;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #44475a;
}

QPushButton:pressed {
    background-color: #32323f;
}

QPushButton#addBtn {
    background-color: #4a6fa5;
}

QPushButton#addBtn:hover {
    background-color: #5c84be;
}

QPushButton#deleteBtn {
    background-color: #c94a53;
}

QPushButton#deleteBtn:hover {
    background-color: #df5b65;
}

/* Kanban Columns Panel */
QFrame#kanbanColumn {
    background-color: %s;
    border: 1px solid #212128;
    border-radius: %s;
}

QFrame#kanbanColumnHeader {
    border: none;
    padding: 8px;
}

QLabel#columnTitle {
    font-weight: bold;
    font-size: 14px;
    color: #ffffff;
}

/* Scroll Area in columns */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #32323f;
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #44475a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
""" % (BG_COLOR, PANEL_BG, TEXT_MAIN, PANEL_BG, BORDER_RADIUS_PANEL)

# Styling for individual Task Cards depending on priority
CARD_STYLE_HIGH = """
QFrame#taskCard {
    background-color: #2d1e22;
    border-left: 5px solid #ff5555;
    border-top: 1px solid #442a2f;
    border-right: 1px solid #442a2f;
    border-bottom: 1px solid #442a2f;
    border-radius: 8px;
    padding: 10px;
}
QFrame#taskCard:hover {
    background-color: #3d2a2f;
}
"""

CARD_STYLE_MEDIUM = """
QFrame#taskCard {
    background-color: #2d261e;
    border-left: 5px solid #ffb86c;
    border-top: 1px solid #44372a;
    border-right: 1px solid #44372a;
    border-bottom: 1px solid #44372a;
    border-radius: 8px;
    padding: 10px;
}
QFrame#taskCard:hover {
    background-color: #3d332a;
}
"""

CARD_STYLE_LOW = """
QFrame#taskCard {
    background-color: #1d2533;
    border-left: 5px solid #8be9fd;
    border-top: 1px solid #273449;
    border-right: 1px solid #273449;
    border-bottom: 1px solid #273449;
    border-radius: 8px;
    padding: 10px;
}
QFrame#taskCard:hover {
    background-color: #273244;
}
"""
