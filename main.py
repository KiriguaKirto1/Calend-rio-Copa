from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Calendário da Copa 2026")
    app.setOrganizationName("Projeto Escolar")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
