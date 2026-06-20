from __future__ import annotations

import math
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QPointF, QRect, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QPolygonF, QRadialGradient
from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget
)

from .icons import icon, icon_size
from .models import Match
from .paths import FLAGS_CACHE_DIR
from .theme import Theme


def vline() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.VLine)
    line.setStyleSheet(f"color: {Theme.LINE}; background: {Theme.LINE}; max-width:1px;")
    return line


def hline() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {Theme.LINE}; background: {Theme.LINE}; max-height:1px;")
    return line


def label(text: str, object_name: str = "") -> QLabel:
    lbl = QLabel(text)
    if object_name:
        lbl.setObjectName(object_name)
    lbl.setWordWrap(True)
    return lbl


def card_layout(frame: QFrame, margins=(18, 18, 18, 18), spacing=12) -> QVBoxLayout:
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return layout


class AppBackground(QWidget):
    """Fundo feito por código: não depende de imagem ou assets."""

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        base = QLinearGradient(0, 0, rect.width(), rect.height())
        if Theme.MODE == "claro":
            base.setColorAt(0.0, QColor("#dbe7ef"))
            base.setColorAt(0.45, QColor("#edf5f9"))
            base.setColorAt(1.0, QColor("#cfe1ea"))
        else:
            base.setColorAt(0.0, QColor("#050b12"))
            base.setColorAt(0.45, QColor("#071421"))
            base.setColorAt(1.0, QColor("#091827"))
        painter.fillRect(rect, base)

        # atmosfera de estádio no topo
        top = QRectF(0, 0, rect.width(), min(rect.height() * 0.40, 330))
        stadium = QLinearGradient(0, 0, rect.width(), top.height())
        if Theme.MODE == "claro":
            stadium.setColorAt(0, QColor(235, 249, 242, 220))
            stadium.setColorAt(0.55, QColor(204, 234, 222, 170))
            stadium.setColorAt(1, QColor(227, 239, 246, 220))
        else:
            stadium.setColorAt(0, QColor(7, 16, 24, 230))
            stadium.setColorAt(0.55, QColor(12, 42, 55, 145))
            stadium.setColorAt(1, QColor(8, 13, 20, 230))
        painter.fillRect(top, stadium)

        # luzes discretas de estádio
        for i, x in enumerate((0.10, 0.25, 0.52, 0.75, 0.90)):
            cx = rect.width() * x
            radial = QRadialGradient(QPointF(cx, 66), 210)
            radial.setColorAt(0, QColor(125, 255, 192, 44 if i % 2 == 0 else 30))
            radial.setColorAt(1, QColor(125, 255, 192, 0))
            painter.fillRect(QRectF(cx - 220, -20, 440, 260), radial)
            painter.setPen(QPen(QColor(226, 246, 255, 42), 1))
            painter.drawLine(int(cx), 42, int(cx - 170), int(top.height()))
            painter.drawLine(int(cx), 42, int(cx + 170), int(top.height()))

        # linhas do campo no rodapé
        painter.setPen(QPen(QColor(34, 197, 94, 24), 2))
        y = rect.height() - 120
        painter.drawArc(QRectF(rect.width() * 0.25, y, rect.width() * 0.5, 170), 0, 180 * 16)
        painter.drawLine(0, rect.height() - 44, rect.width(), rect.height() - 44)
        painter.end()


class FlagBadge(QWidget):
    _pixmap_cache: dict[str, QPixmap] = {}

    def __init__(self, code: str = "", sigla: str = "", size: int = 44, parent=None) -> None:
        super().__init__(parent)
        self.code = code
        self.sigla = sigla or code[:3].upper()
        self._size = size
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(1, 1, self.width() - 2, self.height() - 2)
        path = QPainterPath()
        path.addEllipse(r)
        p.setClipPath(path)
        self._draw_flag(p, r)
        p.setClipping(False)
        p.setPen(QPen(QColor(255, 255, 255, 170), 1.4))
        p.drawEllipse(r)
        p.end()

    def _draw_flag(self, p: QPainter, r: QRectF) -> None:
        code = (self.code or self.sigla or "").strip().upper()
        alias = {
            "BRA": "BR", "FRA": "FR", "ARG": "AR", "MEX": "MX", "NED": "NL",
            "GER": "DE", "ESP": "ES", "ITA": "IT", "USA": "US", "CAN": "CA",
            "POR": "PT", "URU": "UY", "JPN": "JP", "SWE": "SE", "TUR": "TR",
            "PAR": "PY", "CIV": "CI", "CZE": "CZ", "SUI": "CH", "KOR": "KR",
            "MAR": "MA", "SEN": "SN", "ECU": "EC", "QAT": "QA", "BIH": "BA",
            "AUS": "AU", "SCO": "GB-SCT", "ENG": "GB-ENG", "BEL": "BE", "EGY": "EG",
            "IRN": "IR", "NZL": "NZ", "CPV": "CV", "KSA": "SA", "IRQ": "IQ",
            "NOR": "NO", "ALG": "DZ", "AUT": "AT", "JOR": "JO", "COD": "CD",
            "UZB": "UZ", "COL": "CO", "CRO": "HR", "GHA": "GH", "PAN": "PA",
            "HAI": "HT", "RSA": "ZA", "CUW": "CW", "TUN": "TN",
            "CZECHIA": "CZ", "SOUTH KOREA": "KR", "BOSNIA": "BA",
        }
        code = alias.get(code, code)
        pix = self._cached_flag_pixmap(code)
        if not pix.isNull():
            scaled = pix.scaled(int(r.width()), int(r.height()), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            x = int(r.left() + (r.width() - scaled.width()) / 2)
            y = int(r.top() + (r.height() - scaled.height()) / 2)
            p.drawPixmap(x, y, scaled)
            return
        if code == "BR":
            p.fillRect(r, QColor("#169b62"))
            poly = [QPointF(r.center().x(), r.top()+5), QPointF(r.right()-5, r.center().y()), QPointF(r.center().x(), r.bottom()-5), QPointF(r.left()+5, r.center().y())]
            p.setBrush(QColor("#ffdf00")); p.setPen(Qt.PenStyle.NoPen); p.drawPolygon(QPolygonF(poly))
            p.setBrush(QColor("#002776")); p.drawEllipse(QRectF(r.center().x()-r.width()*0.18, r.center().y()-r.height()*0.18, r.width()*0.36, r.height()*0.36))
            return
        if code in {"FR", "IT", "MX", "BE"}:
            colors = {
                "FR": ["#0055a4", "#ffffff", "#ef4135"],
                "IT": ["#009246", "#ffffff", "#ce2b37"],
                "MX": ["#006341", "#ffffff", "#ce1126"],
                "BE": ["#000000", "#ffd90c", "#ef3340"],
            }[code]
            w = r.width()/3
            for i, c in enumerate(colors):
                p.fillRect(QRectF(r.left()+i*w, r.top(), w+1, r.height()), QColor(c))
            return
        if code in {"AR", "UY", "NL", "DE", "ES", "RU", "CO", "HR", "GH", "EG", "IR", "ZA", "KR", "JP", "US", "CA", "PT", "GB-ENG", "GB-SCT", "AU", "TR", "CH", "MA", "SN", "NO", "CZ", "BA", "QA", "HT", "PY", "EC", "CW", "SE", "TN", "CV", "SA", "IQ", "DZ", "AT", "JO", "CD", "UZ", "PA", "CI", "NZ", "IQ", "DZ"}:
            self._draw_common(p, r, code)
            return
        # fallback por código/sigla
        g = QLinearGradient(r.topLeft(), r.bottomRight())
        g.setColorAt(0, QColor("#134e4a")); g.setColorAt(1, QColor("#166534"))
        p.fillRect(r, g)
        p.setPen(QColor("#e8fff3"))
        p.setFont(QFont("Segoe UI", max(8, int(r.width()*0.23)), QFont.Weight.Bold))
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, self.sigla[:3])

    @classmethod
    def _cached_flag_pixmap(cls, code: str) -> QPixmap:
        """Carrega bandeiras PNG geradas automaticamente no cache.

        A V8 usa imagens geradas por código a partir de emoji flags para evitar
        círculos azuis/vazios e deixar as bandeiras mais próximas do visual real,
        sem exigir que o usuário salve assets manualmente.
        """
        if not code:
            return QPixmap()
        if code in cls._pixmap_cache:
            return cls._pixmap_cache[code]
        path = FLAGS_CACHE_DIR / f"{code}.png"
        pix = QPixmap(str(path)) if path.exists() else QPixmap()
        cls._pixmap_cache[code] = pix
        return pix

    def _draw_sigla_overlay(self, p: QPainter, r: QRectF) -> None:
        # Algumas bandeiras simplificadas ficam parecidas com círculos azuis em tamanho pequeno.
        # A sigla deixa claro que é fallback visual, não erro de imagem.
        p.setPen(QColor("#ffffff"))
        p.setFont(QFont("Segoe UI", max(7, int(r.width()*0.18)), QFont.Weight.Bold))
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, self.sigla[:3])

    def _draw_common(self, p: QPainter, r: QRectF, code: str) -> None:
        def hstripe(colors):
            h = r.height() / len(colors)
            for i, c in enumerate(colors):
                p.fillRect(QRectF(r.left(), r.top() + i * h, r.width(), h + 1), QColor(c))

        def vstripe(colors):
            w = r.width() / len(colors)
            for i, c in enumerate(colors):
                p.fillRect(QRectF(r.left() + i * w, r.top(), w + 1, r.height()), QColor(c))

        def star(x: float, y: float, radius: float, color: str = "#ffffff") -> None:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(color))
            pts = []
            for i in range(10):
                ang = -math.pi / 2 + i * math.pi / 5
                rr = radius if i % 2 == 0 else radius * 0.42
                pts.append(QPointF(x + rr * math.cos(ang), y + rr * math.sin(ang)))
            p.drawPolygon(QPolygonF(pts))

        def union_canton() -> None:
            canton = QRectF(r.left(), r.top(), r.width() * 0.48, r.height() * 0.48)
            p.fillRect(canton, QColor("#012169"))
            p.setPen(QPen(QColor("#ffffff"), max(2, r.width() * 0.075)))
            p.drawLine(canton.topLeft(), canton.bottomRight())
            p.drawLine(canton.topRight(), canton.bottomLeft())
            p.setPen(QPen(QColor("#c8102e"), max(1, r.width() * 0.035)))
            p.drawLine(canton.topLeft(), canton.bottomRight())
            p.drawLine(canton.topRight(), canton.bottomLeft())
            p.setPen(Qt.PenStyle.NoPen)
            p.fillRect(QRectF(canton.left(), canton.center().y() - canton.height() * 0.09, canton.width(), canton.height() * 0.18), QColor("#ffffff"))
            p.fillRect(QRectF(canton.center().x() - canton.width() * 0.09, canton.top(), canton.width() * 0.18, canton.height()), QColor("#ffffff"))
            p.fillRect(QRectF(canton.left(), canton.center().y() - canton.height() * 0.045, canton.width(), canton.height() * 0.09), QColor("#c8102e"))
            p.fillRect(QRectF(canton.center().x() - canton.width() * 0.045, canton.top(), canton.width() * 0.09, canton.height()), QColor("#c8102e"))

        if code == "AR":
            hstripe(["#74acdf", "#ffffff", "#74acdf"])
            p.setBrush(QColor("#f6b40e")); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(r.center().x() - 4, r.center().y() - 4, 8, 8))
        elif code == "UY":
            hstripe(["#ffffff", "#0038a8", "#ffffff", "#0038a8", "#ffffff", "#0038a8", "#ffffff"])
            p.fillRect(QRectF(r.left(), r.top(), r.width() * 0.42, r.height() * 0.42), QColor("#ffffff"))
            p.setBrush(QColor("#fcd116")); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(r.left() + 5, r.top() + 5, 10, 10))
        elif code == "NL": hstripe(["#ae1c28", "#ffffff", "#21468b"])
        elif code == "DE": hstripe(["#000000", "#dd0000", "#ffce00"])
        elif code == "ES": hstripe(["#aa151b", "#f1bf00", "#aa151b"])
        elif code == "JP":
            p.fillRect(r, QColor("#ffffff"))
            p.setBrush(QColor("#bc002d")); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(r.center().x() - r.width() * 0.20, r.center().y() - r.height() * 0.20, r.width() * 0.40, r.height() * 0.40))
        elif code == "KR":
            p.fillRect(r, QColor("#ffffff"))
            p.setBrush(QColor("#c60c30")); p.setPen(Qt.PenStyle.NoPen)
            p.drawPie(QRectF(r.center().x() - 10, r.center().y() - 10, 20, 20), 0, 180 * 16)
            p.setBrush(QColor("#003478")); p.drawPie(QRectF(r.center().x() - 10, r.center().y() - 10, 20, 20), 180 * 16, 180 * 16)
            p.setPen(QPen(QColor("#111111"), 1.4))
            p.drawLine(QPointF(r.left()+7, r.top()+8), QPointF(r.left()+15, r.top()+14))
            p.drawLine(QPointF(r.right()-7, r.bottom()-8), QPointF(r.right()-15, r.bottom()-14))
            p.drawLine(QPointF(r.left()+7, r.bottom()-8), QPointF(r.left()+15, r.bottom()-14))
            p.drawLine(QPointF(r.right()-7, r.top()+8), QPointF(r.right()-15, r.top()+14))
        elif code == "US":
            hstripe(["#b22234", "#ffffff"] * 4)
            p.fillRect(QRectF(r.left(), r.top(), r.width() * 0.48, r.height() * 0.48), QColor("#3c3b6e"))
        elif code == "CA":
            vstripe(["#ff0000", "#ffffff", "#ff0000"])
            p.setPen(QColor("#ff0000")); p.setFont(QFont("Segoe UI", max(10, int(r.width()*0.38)), QFont.Weight.Bold)); p.drawText(r, Qt.AlignmentFlag.AlignCenter, "✦")
        elif code == "PT":
            p.fillRect(QRectF(r.left(), r.top(), r.width()*0.42, r.height()), QColor("#006600"))
            p.fillRect(QRectF(r.left()+r.width()*0.42, r.top(), r.width()*0.58, r.height()), QColor("#ff0000"))
            p.setBrush(QColor("#ffcc00")); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(r.left()+r.width()*0.35, r.center().y()-5, 10, 10))
        elif code == "GB-ENG":
            p.fillRect(r, QColor("#ffffff"))
            p.fillRect(QRectF(r.left(), r.center().y()-4, r.width(), 8), QColor("#ce1124"))
            p.fillRect(QRectF(r.center().x()-4, r.top(), 8, r.height()), QColor("#ce1124"))
        elif code == "GB-SCT":
            p.fillRect(r, QColor("#0065bd"))
            p.setPen(QPen(QColor("#ffffff"), 4)); p.drawLine(r.topLeft(), r.bottomRight()); p.drawLine(r.topRight(), r.bottomLeft())
        elif code == "AU":
            p.fillRect(r, QColor("#00008b")); union_canton()
            star(r.left()+r.width()*0.70, r.top()+r.height()*0.62, 4)
            star(r.left()+r.width()*0.76, r.top()+r.height()*0.35, 3)
            star(r.left()+r.width()*0.60, r.top()+r.height()*0.78, 3)
        elif code == "NZ":
            p.fillRect(r, QColor("#00247d")); union_canton()
            for x, y in [(0.70,0.36),(0.80,0.50),(0.66,0.67),(0.78,0.75)]:
                star(r.left()+r.width()*x, r.top()+r.height()*y, 3.4, "#cc142b")
        elif code == "TR":
            p.fillRect(r, QColor("#e30a17")); p.setPen(QColor("#ffffff")); p.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold)); p.drawText(r, Qt.AlignmentFlag.AlignCenter, "☾")
        elif code == "CH":
            p.fillRect(r, QColor("#d52b1e")); p.fillRect(QRectF(r.center().x()-4, r.top()+9, 8, r.height()-18), QColor("#ffffff")); p.fillRect(QRectF(r.left()+9, r.center().y()-4, r.width()-18, 8), QColor("#ffffff"))
        elif code == "MA":
            p.fillRect(r, QColor("#c1272d")); p.setPen(QPen(QColor("#006233"), 2)); p.setFont(QFont("Segoe UI", 15)); p.drawText(r, Qt.AlignmentFlag.AlignCenter, "★")
        elif code == "SN": vstripe(["#00853f", "#fdef42", "#e31b23"]); star(r.center().x(), r.center().y(), 5, "#00853f")
        elif code == "NO":
            p.fillRect(r, QColor("#ba0c2f")); p.fillRect(QRectF(r.left()+r.width()*0.28, r.top(), r.width()*0.16, r.height()), QColor("#ffffff")); p.fillRect(QRectF(r.left(), r.top()+r.height()*0.40, r.width(), r.height()*0.16), QColor("#ffffff")); p.fillRect(QRectF(r.left()+r.width()*0.32, r.top(), r.width()*0.08, r.height()), QColor("#00205b")); p.fillRect(QRectF(r.left(), r.top()+r.height()*0.44, r.width(), r.height()*0.08), QColor("#00205b"))
        elif code == "CO": hstripe(["#fcd116", "#003893", "#ce1126"])
        elif code == "HR": hstripe(["#ff0000", "#ffffff", "#171796"])
        elif code == "GH": hstripe(["#ce1126", "#fcd116", "#006b3f"]); star(r.center().x(), r.center().y(), 5, "#000000")
        elif code == "EG": hstripe(["#ce1126", "#ffffff", "#000000"])
        elif code == "IR": hstripe(["#239f40", "#ffffff", "#da0000"])
        elif code == "ZA": hstripe(["#de3831", "#ffffff", "#002395", "#007a4d"])
        elif code == "CZ":
            hstripe(["#ffffff", "#d7141a"])
            p.setBrush(QColor("#11457e")); p.setPen(Qt.PenStyle.NoPen)
            p.drawPolygon(QPolygonF([QPointF(r.left(), r.top()), QPointF(r.center().x(), r.center().y()), QPointF(r.left(), r.bottom())]))
        elif code == "BA":
            p.fillRect(r, QColor("#002f6c")); p.setBrush(QColor("#fcd116")); p.setPen(Qt.PenStyle.NoPen)
            p.drawPolygon(QPolygonF([QPointF(r.right(), r.top()), QPointF(r.right(), r.bottom()), QPointF(r.left()+r.width()*0.42, r.top())]))
            for i in range(4): star(r.left()+r.width()*(0.20+i*0.13), r.top()+r.height()*(0.25+i*0.12), 2.2)
        elif code == "QA":
            p.fillRect(r, QColor("#8a1538"))
            p.setBrush(QColor("#ffffff")); p.setPen(Qt.PenStyle.NoPen)
            pts = [QPointF(r.left(), r.top())]
            teeth = 6
            for i in range(teeth):
                y1 = r.top() + i * r.height()/teeth
                y2 = r.top() + (i+0.5) * r.height()/teeth
                pts.append(QPointF(r.left()+r.width()*0.28, y2))
                pts.append(QPointF(r.left(), y1 + r.height()/teeth))
            pts.append(QPointF(r.left(), r.bottom()))
            p.drawPolygon(QPolygonF(pts))
        elif code == "HT":
            hstripe(["#00209f", "#d21034"])
            p.fillRect(QRectF(r.center().x()-6, r.center().y()-4, 12, 8), QColor("#ffffff"))
        elif code == "PY": hstripe(["#d52b1e", "#ffffff", "#0038a8"])
        elif code == "EC": hstripe(["#ffdd00", "#034ea2", "#ed1c24"])
        elif code == "CW":
            p.fillRect(r, QColor("#002b7f")); p.fillRect(QRectF(r.left(), r.top()+r.height()*0.62, r.width(), r.height()*0.12), QColor("#f9e814"))
            star(r.left()+r.width()*0.36, r.top()+r.height()*0.28, 4); star(r.left()+r.width()*0.49, r.top()+r.height()*0.34, 3)
        elif code == "SE":
            p.fillRect(r, QColor("#006aa7")); p.fillRect(QRectF(r.left()+r.width()*0.30, r.top(), r.width()*0.14, r.height()), QColor("#fecc00")); p.fillRect(QRectF(r.left(), r.top()+r.height()*0.42, r.width(), r.height()*0.14), QColor("#fecc00"))
        elif code == "TN":
            p.fillRect(r, QColor("#e70013")); p.setBrush(QColor("#ffffff")); p.setPen(Qt.PenStyle.NoPen); p.drawEllipse(QRectF(r.center().x()-10, r.center().y()-10, 20, 20)); p.setPen(QColor("#e70013")); p.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold)); p.drawText(r, Qt.AlignmentFlag.AlignCenter, "☾")
        elif code == "CV": hstripe(["#003893", "#003893", "#ffffff", "#cf2027", "#ffffff", "#003893"]); star(r.left()+r.width()*0.35, r.center().y(), 4, "#f7d116")
        elif code == "SA":
            p.fillRect(r, QColor("#006c35")); p.setPen(QPen(QColor("#ffffff"), 2)); p.drawLine(QPointF(r.left()+8, r.bottom()-11), QPointF(r.right()-8, r.bottom()-11)); p.setFont(QFont("Segoe UI", max(8, int(r.width()*0.22)), QFont.Weight.Bold)); p.drawText(QRectF(r.left()+2, r.top()+8, r.width()-4, r.height()/2), Qt.AlignmentFlag.AlignCenter, "SA")
        elif code == "IQ": hstripe(["#ce1126", "#ffffff", "#000000"]); p.setPen(QColor("#007a3d")); p.drawText(r, Qt.AlignmentFlag.AlignCenter, "★")
        elif code == "DZ": vstripe(["#006233", "#ffffff"]); p.setPen(QColor("#d21034")); p.setFont(QFont("Segoe UI", 14)); p.drawText(r, Qt.AlignmentFlag.AlignCenter, "☾")
        elif code == "AT": hstripe(["#ed2939", "#ffffff", "#ed2939"])
        elif code == "JO":
            hstripe(["#000000", "#ffffff", "#007a3d"]); p.setBrush(QColor("#ce1126")); p.setPen(Qt.PenStyle.NoPen); p.drawPolygon(QPolygonF([QPointF(r.left(), r.top()), QPointF(r.center().x(), r.center().y()), QPointF(r.left(), r.bottom())])); star(r.left()+r.width()*0.22, r.center().y(), 3.5)
        elif code == "CD": p.fillRect(r, QColor("#00a3e0")); p.setPen(QPen(QColor("#ce1021"), 7)); p.drawLine(r.bottomLeft(), r.topRight()); p.setPen(QPen(QColor("#f7d618"), 12)); p.drawPoint(int(r.left()+r.width()*0.25), int(r.top()+r.height()*0.25))
        elif code == "UZ": hstripe(["#1eb5e5", "#ffffff", "#009639"]); p.setPen(QColor("#ce1126")); p.drawLine(int(r.left()), int(r.center().y()), int(r.right()), int(r.center().y()))
        elif code == "PA": vstripe(["#ffffff", "#d21034"]); p.fillRect(QRectF(r.left(), r.center().y(), r.width()/2, r.height()/2), QColor("#005293"))
        elif code == "CI": vstripe(["#f77f00", "#ffffff", "#009e60"])
        else:
            p.fillRect(r, QColor("#134e4a"))


class StadiumPreview(QFrame):
    def __init__(self, title: str, subtitle: str = "", image_path: str = "", parent=None) -> None:
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.image_path = image_path
        self.setMinimumHeight(190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setObjectName("SoftCard")

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath(); path.addRoundedRect(r, 14, 14)
        p.setClipPath(path)

        pix = QPixmap(self.image_path) if self.image_path else QPixmap()
        if not pix.isNull():
            scaled = pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap(0, 0, scaled)
        else:
            g = QLinearGradient(r.topLeft(), r.bottomRight())
            g.setColorAt(0, QColor("#102033")); g.setColorAt(0.5, QColor("#153548")); g.setColorAt(1, QColor("#0b141f"))
            p.fillRect(r, g)
            # arquibancada e gramado gerados por código
            p.setPen(QPen(QColor(255,255,255,30), 1))
            for i in range(8):
                y = r.top() + 38 + i*10
                p.drawArc(QRectF(r.left()+25+i*8, y, r.width()-50-i*16, 70+i*9), 0, 180*16)
            field = QLinearGradient(0, r.bottom()-60, 0, r.bottom())
            field.setColorAt(0, QColor("#123b2a")); field.setColorAt(1, QColor("#0a2219"))
            p.fillRect(QRectF(r.left(), r.bottom()-62, r.width(), 62), field)
            p.setPen(QPen(QColor(34,197,94,70), 2))
            p.drawLine(int(r.left()+20), int(r.bottom()-30), int(r.right()-20), int(r.bottom()-30))
            p.drawEllipse(QRectF(r.center().x()-44, r.bottom()-52, 88, 44))

        overlay = QLinearGradient(0, r.top(), 0, r.bottom())
        overlay.setColorAt(0, QColor(0,0,0,10)); overlay.setColorAt(1, QColor(0,0,0,190))
        p.fillRect(r, overlay)
        p.setClipping(False)
        p.setPen(QPen(QColor(34,197,94,120), 1.4))
        p.drawRoundedRect(r, 14, 14)
        p.setPen(QColor("#f4f8fb"))
        p.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        p.drawText(QRectF(18, self.height()-58, self.width()-36, 24), Qt.AlignmentFlag.AlignLeft, self.title)
        p.setPen(QColor("#9fb0c3"))
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(QRectF(18, self.height()-32, self.width()-36, 20), Qt.AlignmentFlag.AlignLeft, self.subtitle)
        p.end()


class StatCard(QFrame):
    def __init__(self, title: str, value: str, caption: str, icon_name: str, color: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumHeight(128)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24); shadow.setOffset(0, 8); shadow.setColor(QColor(0,0,0,70))
        self.setGraphicsEffect(shadow)
        lay = QVBoxLayout(self); lay.setContentsMargins(18,16,18,16); lay.setSpacing(8)
        row = QHBoxLayout(); row.setSpacing(8)
        ico = QLabel(); ico.setPixmap(icon(icon_name, color, 22).pixmap(24,24)); row.addWidget(ico)
        t = QLabel(title); t.setStyleSheet(f"color:{color}; font-size:12px; font-weight:900; letter-spacing:.8px;"); row.addWidget(t); row.addStretch()
        lay.addLayout(row)
        v = QLabel(value); v.setStyleSheet("font-size:34px; font-weight:900;"); lay.addWidget(v)
        c = QLabel(caption); c.setObjectName("SmallMuted"); lay.addWidget(c)


class PhaseChip(QLabel):
    def __init__(self, text: str, color: str | None = None, parent=None) -> None:
        super().__init__(text, parent)
        c = color or Theme.phase_color(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"background: {c}22; color: {c}; border: 1px solid {c}66; border-radius: 9px; padding: 4px 8px; font-weight:800; font-size:11px;")


class MatchRow(QFrame):
    details_requested = Signal(str)

    def __init__(self, match: Match, compact: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.match = match
        self.setObjectName("SoftCard")
        self.setMinimumHeight(72 if compact else 86)
        lay = QHBoxLayout(self); lay.setContentsMargins(14,10,14,10); lay.setSpacing(14)

        left = self._team_block(match.time_a, match.pais_a, match.sigla_a, align_left=True)
        right = self._team_block(match.time_b, match.pais_b, match.sigla_b, align_left=False)
        center = QVBoxLayout(); center.setSpacing(2)
        time = QLabel(match.hora); time.setAlignment(Qt.AlignmentFlag.AlignCenter); time.setStyleSheet(f"color:{Theme.GREEN}; font-size:18px; font-weight:900;")
        date = QLabel(match.short_date); date.setAlignment(Qt.AlignmentFlag.AlignCenter); date.setObjectName("SmallMuted")
        stadium = QLabel(match.estadio); stadium.setAlignment(Qt.AlignmentFlag.AlignCenter); stadium.setObjectName("SmallMuted")
        group = PhaseChip(match.grupo if compact else match.fase)
        center.addWidget(time); center.addWidget(date); center.addWidget(stadium); center.addWidget(group)

        lay.addLayout(left, 2)
        lay.addLayout(center, 1)
        lay.addLayout(right, 2)
        btn = QPushButton("Detalhes")
        btn.setObjectName("GhostButton")
        btn.setIcon(icon("next", Theme.GREEN, 12)); btn.setIconSize(icon_size(12))
        btn.clicked.connect(lambda: self.details_requested.emit(match.id))
        lay.addWidget(btn)

    def _team_block(self, team: str, country_code: str, sigla: str, align_left: bool) -> QHBoxLayout:
        row = QHBoxLayout(); row.setSpacing(9)
        flag = FlagBadge(country_code, sigla, 40)
        texts = QVBoxLayout(); texts.setSpacing(2)
        name = QLabel(team); name.setStyleSheet("font-size:14px; font-weight:900;")
        sg = QLabel(sigla); sg.setObjectName("SmallMuted")
        if not align_left:
            name.setAlignment(Qt.AlignmentFlag.AlignRight); sg.setAlignment(Qt.AlignmentFlag.AlignRight)
        texts.addWidget(name); texts.addWidget(sg)
        if align_left:
            row.addWidget(flag); row.addLayout(texts); row.addStretch()
        else:
            row.addStretch(); row.addLayout(texts); row.addWidget(flag)
        return row


class BottomNav(QFrame):
    page_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.buttons: dict[str, QPushButton] = {}
        lay = QHBoxLayout(self); lay.setContentsMargins(10,8,10,8); lay.setSpacing(8)
        items = [
            ("dashboard", "Início", "home"),
            ("games", "Jogos", "games"),
            ("calendar", "Calendário", "calendar"),
            ("favorites", "Favoritos", "star"),
            ("settings", "Mais", "more"),
        ]
        for page, text, icon_name in items:
            btn = QPushButton(text)
            btn.setObjectName("NavButton")
            btn.setIcon(icon(icon_name, Theme.MUTED, 16)); btn.setIconSize(icon_size(16))
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked=False, p=page: self.page_requested.emit(p))
            self.buttons[page] = btn
            lay.addWidget(btn)
        self.set_active("dashboard")

    def set_active(self, page: str) -> None:
        for key, btn in self.buttons.items():
            active = key == page
            btn.setProperty("active", "true" if active else "false")
            btn.setIcon(icon(self._icon_name(key), Theme.GREEN if active else Theme.MUTED, 16))
            btn.style().unpolish(btn); btn.style().polish(btn)

    @staticmethod
    def _icon_name(page: str) -> str:
        return {"dashboard":"home", "games":"games", "calendar":"calendar", "favorites":"star", "settings":"more"}.get(page, "more")


class HeaderBar(QFrame):
    export_requested = Signal()
    refresh_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SoftCard")
        lay = QHBoxLayout(self); lay.setContentsMargins(16,10,16,10); lay.setSpacing(12)
        logo = QLabel(); logo.setPixmap(icon("trophy", Theme.GREEN, 20).pixmap(24,24)); lay.addWidget(logo)
        title = QLabel("Calendário da Copa 2026"); title.setStyleSheet("font-weight:900; font-size:16px;"); lay.addWidget(title)
        lay.addStretch()
        reload_btn = QPushButton("Recarregar dados")
        reload_btn.setObjectName("GhostButton")
        reload_btn.setToolTip("Recarrega os arquivos JSON locais. Não é atualização em tempo real pela internet.")
        reload_btn.setIcon(icon("refresh", Theme.GREEN, 14)); reload_btn.setIconSize(icon_size(14))
        reload_btn.clicked.connect(self.refresh_requested.emit)
        lay.addWidget(reload_btn)
        btn = QPushButton("Baixar calendário")
        btn.setObjectName("PrimaryButton")
        btn.setToolTip("Gera o arquivo .ics e tenta abrir no calendário padrão do sistema.")
        btn.setIcon(icon("download", "#03140a", 14)); btn.setIconSize(icon_size(14))
        btn.clicked.connect(self.export_requested.emit)
        lay.addWidget(btn)
