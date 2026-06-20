from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF


def _pen(color: str, width: float = 2.0) -> QPen:
    pen = QPen(QColor(color), width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def app_icon(size: int = 64) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(QColor("transparent"))
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#22c55e"))
    p.setPen(_pen("#bbf7d0", max(2, size / 20)))
    p.drawRoundedRect(QRectF(size * 0.10, size * 0.10, size * 0.80, size * 0.80), size * 0.18, size * 0.18)
    p.setPen(_pen("#071018", max(2, size / 15)))
    p.drawEllipse(QRectF(size * 0.28, size * 0.28, size * 0.44, size * 0.44))
    p.drawLine(QPointF(size * 0.50, size * 0.22), QPointF(size * 0.50, size * 0.78))
    p.drawLine(QPointF(size * 0.22, size * 0.50), QPointF(size * 0.78, size * 0.50))
    p.end()
    return QIcon(pix)


def icon(name: str, color: str = "#f4f8fb", size: int = 18) -> QIcon:
    """Ícones desenhados por código para evitar emojis/ícones Qt inconsistentes."""
    s = max(14, int(size))
    pix = QPixmap(s, s)
    pix.fill(QColor("transparent"))
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(color)
    pen = _pen(color, max(1.6, s / 10))
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    m = s * 0.15
    r = QRectF(m, m, s - 2 * m, s - 2 * m)
    cx, cy = s / 2, s / 2

    if name == "home":
        p.drawPolyline([QPointF(s*0.18, s*0.52), QPointF(cx, s*0.22), QPointF(s*0.82, s*0.52)])
        p.drawRoundedRect(QRectF(s*0.28, s*0.50, s*0.44, s*0.34), 2, 2)
    elif name == "games":
        p.drawEllipse(r)
        p.drawLine(QPointF(cx, r.top()), QPointF(cx, r.bottom()))
        p.drawLine(QPointF(r.left(), cy), QPointF(r.right(), cy))
        p.drawArc(r.adjusted(s*0.12, 0, -s*0.12, 0), 80*16, 200*16)
    elif name == "calendar" or name == "calendar_plus":
        p.drawRoundedRect(QRectF(s*0.20, s*0.24, s*0.60, s*0.56), 2.5, 2.5)
        p.drawLine(QPointF(s*0.20, s*0.40), QPointF(s*0.80, s*0.40))
        p.drawLine(QPointF(s*0.34, s*0.18), QPointF(s*0.34, s*0.31))
        p.drawLine(QPointF(s*0.66, s*0.18), QPointF(s*0.66, s*0.31))
        if name == "calendar_plus":
            p.drawLine(QPointF(cx, s*0.51), QPointF(cx, s*0.70)); p.drawLine(QPointF(s*0.40, s*0.60), QPointF(s*0.60, s*0.60))
    elif name == "star":
        pts = [QPointF(cx, s*0.18), QPointF(s*0.59, s*0.41), QPointF(s*0.84, s*0.42), QPointF(s*0.64, s*0.58), QPointF(s*0.71, s*0.82), QPointF(cx, s*0.68), QPointF(s*0.29, s*0.82), QPointF(s*0.36, s*0.58), QPointF(s*0.16, s*0.42), QPointF(s*0.41, s*0.41)]
        p.drawPolygon(QPolygonF(pts))
    elif name == "more":
        p.setBrush(c); p.setPen(Qt.PenStyle.NoPen)
        for x in (0.32, 0.50, 0.68): p.drawEllipse(QRectF(s*x-s*0.045, cy-s*0.045, s*0.09, s*0.09))
    elif name == "settings":
        p.drawEllipse(QRectF(s*0.34, s*0.34, s*0.32, s*0.32))
        for angle in range(0, 360, 60):
            import math
            a = math.radians(angle)
            p.drawLine(QPointF(cx + s*0.23*math.cos(a), cy + s*0.23*math.sin(a)), QPointF(cx + s*0.36*math.cos(a), cy + s*0.36*math.sin(a)))
    elif name == "search":
        p.drawEllipse(QRectF(s*0.20, s*0.20, s*0.42, s*0.42)); p.drawLine(QPointF(s*0.56, s*0.56), QPointF(s*0.80, s*0.80))
    elif name == "stadium":
        p.drawArc(QRectF(s*0.18, s*0.25, s*0.64, s*0.45), 0, 180*16)
        p.drawRoundedRect(QRectF(s*0.20, s*0.45, s*0.60, s*0.25), 2, 2)
        p.drawLine(QPointF(s*0.30, s*0.45), QPointF(s*0.30, s*0.70)); p.drawLine(QPointF(s*0.70, s*0.45), QPointF(s*0.70, s*0.70))
    elif name == "clock":
        p.drawEllipse(r); p.drawLine(QPointF(cx, cy), QPointF(cx, s*0.30)); p.drawLine(QPointF(cx, cy), QPointF(s*0.66, s*0.62))
    elif name == "bell":
        p.drawArc(QRectF(s*0.27, s*0.25, s*0.46, s*0.50), 20*16, 140*16)
        p.drawLine(QPointF(s*0.28, s*0.62), QPointF(s*0.72, s*0.62)); p.drawArc(QRectF(s*0.42, s*0.63, s*0.16, s*0.14), 180*16, 180*16)
    elif name in {"export", "download"}:
        p.drawRoundedRect(QRectF(s*0.22, s*0.54, s*0.56, s*0.24), 2, 2)
        p.drawLine(QPointF(cx, s*0.20), QPointF(cx, s*0.57))
        p.drawPolyline([QPointF(s*0.36, s*0.43), QPointF(cx, s*0.58), QPointF(s*0.64, s*0.43)])
    elif name == "filter":
        p.drawPolyline([QPointF(s*0.20, s*0.26), QPointF(s*0.80, s*0.26), QPointF(s*0.58, s*0.52), QPointF(s*0.58, s*0.75), QPointF(s*0.42, s*0.82), QPointF(s*0.42, s*0.52), QPointF(s*0.20, s*0.26)])
    elif name == "refresh":
        p.drawArc(QRectF(s*0.22, s*0.22, s*0.56, s*0.56), 30*16, 270*16)
        p.drawPolyline([QPointF(s*0.70, s*0.20), QPointF(s*0.80, s*0.40), QPointF(s*0.58, s*0.36)])
    elif name == "folder":
        p.drawRoundedRect(QRectF(s*0.16, s*0.32, s*0.68, s*0.44), 2.5, 2.5)
        p.drawPolyline([QPointF(s*0.18, s*0.34), QPointF(s*0.36, s*0.34), QPointF(s*0.42, s*0.25), QPointF(s*0.62, s*0.25), QPointF(s*0.68, s*0.34)])
    elif name == "info":
        p.drawEllipse(r); p.drawLine(QPointF(cx, s*0.46), QPointF(cx, s*0.70)); p.drawPoint(QPointF(cx, s*0.32))
    elif name == "back":
        p.drawPolyline([QPointF(s*0.62, s*0.22), QPointF(s*0.34, cy), QPointF(s*0.62, s*0.78)])
    elif name == "next":
        p.drawPolyline([QPointF(s*0.38, s*0.22), QPointF(s*0.66, cy), QPointF(s*0.38, s*0.78)])
    elif name == "trophy":
        p.drawRoundedRect(QRectF(s*0.34, s*0.22, s*0.32, s*0.28), 3, 3)
        p.drawArc(QRectF(s*0.18, s*0.25, s*0.20, s*0.20), 270*16, -170*16)
        p.drawArc(QRectF(s*0.62, s*0.25, s*0.20, s*0.20), 270*16, 170*16)
        p.drawLine(QPointF(cx, s*0.50), QPointF(cx, s*0.70))
        p.drawLine(QPointF(s*0.34, s*0.78), QPointF(s*0.66, s*0.78))
    else:
        p.drawEllipse(r)
    p.end()
    return QIcon(pix)


def icon_size(size: int = 18) -> QSize:
    return QSize(size, size)
