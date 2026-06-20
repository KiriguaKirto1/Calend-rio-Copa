from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


def open_file(path: Path) -> bool:
    """Abre um arquivo no aplicativo padrão do sistema operacional.

    No Windows, isso costuma abrir arquivos .ics no aplicativo de calendário
    associado. O sistema operacional ainda pode pedir confirmação de importação.
    """
    target = Path(path).resolve()
    if not target.exists():
        return False
    try:
        if QDesktopServices.openUrl(QUrl.fromLocalFile(str(target))):
            return True
    except Exception:
        pass
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(target))  # type: ignore[attr-defined]
            return True
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(target)])
            return True
        subprocess.Popen(["xdg-open", str(target)])
        return True
    except Exception:
        return False


def open_folder(path: Path) -> bool:
    target = Path(path).resolve()
    if target.is_file():
        target = target.parent
    if not target.exists():
        return False
    return open_file(target)
