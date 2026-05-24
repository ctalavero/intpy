import sys
from pathlib import Path

# Add project root directory to sys.path to allow launching directly as a script file
sys.path.append(str(Path(__file__).resolve().parents[2]))

import argparse
from PySide6.QtWidgets import QApplication
from intpy.gui.main_window import MainWindow
from intpy.gui.style import QSS_STYLESHEET



def main() -> None:
    # 1. Parse DB argument for compatibility with TaskHub CLI config
    parser = argparse.ArgumentParser(description="TaskHub GUI - Kanban Board")
    parser.add_argument(
        "--db",
        type=str,
        default="tasks.json",
        help="Path to the JSON database file."
    )
    # Safely parse only known args so PySide doesn't crash on standard QT flags
    args, unknown = parser.parse_known_args()

    # 2. Boot QApplication
    # Pass unknown args + sys.argv[0] to Qt so it respects default Qt flags
    qt_args = [sys.argv[0]] + unknown
    app = QApplication(qt_args)
    
    # 3. Apply Premium Dark Mode Style Sheet globally
    app.setStyleSheet(QSS_STYLESHEET)

    # 4. Instantiate and launch MainWindow
    window = MainWindow(db_path=args.db)
    window.show()

    # 5. Execute Loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
