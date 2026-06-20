from __future__ import annotations


class Theme:
    MODE = "escuro"
    BG = "#071018"
    BG_2 = "#0b1622"
    SURFACE = "#101c28"
    SURFACE_2 = "#132333"
    LINE = "#243242"
    TEXT = "#f4f8fb"
    MUTED = "#9fb0c3"
    GREEN = "#22c55e"
    GREEN_2 = "#16a34a"
    CYAN = "#38bdf8"
    BLUE = "#2563eb"
    ORANGE = "#f59e0b"
    PURPLE = "#8b5cf6"
    RED = "#ef4444"
    YELLOW = "#facc15"
    COMPACT = False

    ACCENTS = {
        "verde": ("#22c55e", "#16a34a"),
        "azul": ("#38bdf8", "#0284c7"),
        "roxo": ("#8b5cf6", "#7c3aed"),
        "laranja": ("#f59e0b", "#d97706"),
        "vermelho": ("#ef4444", "#dc2626"),
    }

    @classmethod
    def apply_preferences(cls, preferences: dict | None = None) -> None:
        """Aplica preferências visuais em tempo de execução.

        A partir da V7, tema claro, cor de destaque e visualização compacta
        alteram a interface de forma visível e testável.
        """
        preferences = preferences or {}
        cls.MODE = "claro" if str(preferences.get("tema", "escuro")).lower() == "claro" else "escuro"
        accent = str(preferences.get("cor_destaque", "verde")).lower()
        cls.GREEN, cls.GREEN_2 = cls.ACCENTS.get(accent, cls.ACCENTS["verde"])
        cls.COMPACT = bool(preferences.get("visual_compacto", False))
        if cls.MODE == "claro":
            cls.BG = "#dbe7ef"
            cls.BG_2 = "#edf5f9"
            cls.SURFACE = "#ffffff"
            cls.SURFACE_2 = "#eaf2f7"
            cls.LINE = "#b6c7d4"
            cls.TEXT = "#0f172a"
            cls.MUTED = "#475569"
        else:
            cls.BG = "#071018"
            cls.BG_2 = "#0b1622"
            cls.SURFACE = "#101c28"
            cls.SURFACE_2 = "#132333"
            cls.LINE = "#243242"
            cls.TEXT = "#f4f8fb"
            cls.MUTED = "#9fb0c3"

    @classmethod
    def row_height(cls, normal: int = 62, compact: int = 50) -> int:
        return compact if cls.COMPACT else normal

    @staticmethod
    def phase_color(phase: str) -> str:
        mapping = {
            "Grupos": Theme.BLUE,
            "Fase de grupos": Theme.BLUE,
            "32 avos": Theme.ORANGE,
            "16 avos": Theme.ORANGE,
            "Oitavas": Theme.ORANGE,
            "Quartas": Theme.ORANGE,
            "Quarterfinal": Theme.ORANGE,
            "Round Of 32": Theme.ORANGE,
            "Round Of 16": Theme.ORANGE,
            "Round of 32": Theme.ORANGE,
            "Round of 16": Theme.ORANGE,
            "Mata-mata": Theme.ORANGE,
            "Semifinal": Theme.PURPLE,
            "3º lugar": Theme.YELLOW,
            "Final": Theme.RED,
        }
        return mapping.get(phase, Theme.GREEN)

    @staticmethod
    def global_qss() -> str:
        if Theme.MODE == "claro":
            card_bg = "rgba(255,255,255,0.92)"
            featured_bg = "rgba(246,252,248,0.96)"
            hero_bg = "rgba(255,255,255,0.70)"
            soft_bg = "rgba(239,248,244,0.82)"
            inline_bg = "rgba(255,255,255,0.66)"
            match_bg = "rgba(255,255,255,0.78)"
            match_hover = "rgba(238,250,243,0.96)"
            table_bg = "rgba(232,242,248,0.80)"
            day_bg = "rgba(255,255,255,0.56)"
            day_sel = "rgba(34,197,94,0.16)"
            input_bg = "rgba(255,255,255,0.96)"
            hover_bg = "#e6f6ee"
            ghost_bg = "rgba(34,197,94,0.12)"
            accent_bg = "rgba(255,255,255,0.72)"
        else:
            card_bg = "rgba(16, 28, 40, 0.92)"
            featured_bg = "rgba(13, 25, 36, 0.96)"
            hero_bg = "rgba(12, 24, 36, 0.74)"
            soft_bg = "rgba(19, 35, 51, 0.78)"
            inline_bg = "rgba(19, 35, 51, 0.68)"
            match_bg = "rgba(19, 35, 51, 0.82)"
            match_hover = "rgba(21, 43, 58, 0.88)"
            table_bg = "rgba(9, 18, 28, 0.74)"
            day_bg = "rgba(19, 35, 51, 0.58)"
            day_sel = "rgba(34, 197, 94, 0.10)"
            input_bg = "rgba(9, 18, 28, 0.94)"
            hover_bg = "#193047"
            ghost_bg = "rgba(34, 197, 94, 0.08)"
            accent_bg = "rgba(9, 18, 28, 0.72)"
        return f"""
        * {{
            font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            color: {Theme.TEXT};
        }}
        QMainWindow, QWidget#Root {{
            background: {Theme.BG};
        }}
        QFrame#Card, QFrame.Card {{
            background-color: {card_bg};
            border: 1px solid {Theme.LINE};
            border-radius: 16px;
        }}
        QFrame#FeaturedCard {{
            background-color: {featured_bg};
            border: 1px solid {Theme.GREEN};
            border-radius: 18px;
        }}
        QFrame#HeroCard {{
            background-color: {hero_bg};
            border: 1px solid rgba(56, 189, 248, 0.22);
            border-radius: 16px;
        }}
        QFrame#SoftCard {{
            background-color: {soft_bg};
            border: 1px solid {Theme.LINE};
            border-radius: 13px;
        }}
        QFrame#InlineInfo {{
            background-color: {inline_bg};
            border: 1px solid rgba(127,127,127,0.12);
            border-radius: 12px;
        }}
        QFrame#MatchRow {{
            background-color: {match_bg};
            border: 1px solid rgba(127, 127, 127, 0.12);
            border-radius: 14px;
        }}
        QFrame#MatchRow:hover {{
            border-color: {Theme.GREEN};
            background-color: {match_hover};
        }}
        QFrame#TableHeader {{
            background-color: {table_bg};
            border: 1px solid rgba(127,127,127,0.10);
            border-radius: 12px;
        }}
        QFrame#PhaseTile {{
            background-color: {soft_bg};
            border: 1px solid rgba(127,127,127,0.12);
            border-radius: 13px;
        }}
        QFrame#CalendarDay {{
            background-color: {day_bg};
            border: 1px solid rgba(127, 127, 127, 0.10);
            border-radius: 12px;
        }}
        QFrame#CalendarDay[selected="true"] {{
            border: 1px solid {Theme.GREEN};
            background-color: {day_sel};
        }}
        QFrame#CalendarDay[empty="true"] {{
            background-color: rgba(127, 127, 127, 0.06);
            border: 1px solid rgba(127, 127, 127, 0.05);
        }}
        QLabel#Title, QLabel#PageTitle {{
            font-size: 28px;
            font-weight: 850;
            color: {Theme.TEXT};
        }}
        QLabel#Subtitle {{
            font-size: 14px;
            color: {Theme.MUTED};
        }}
        QLabel#Muted {{ color: {Theme.MUTED}; }}
        QLabel#SmallMuted {{
            color: {Theme.MUTED};
            font-size: 12px;
        }}
        QLabel#SectionTitle {{
            font-size: 15px;
            font-weight: 850;
            letter-spacing: 0.5px;
        }}
        QPushButton {{
            background-color: {Theme.SURFACE_2};
            border: 1px solid {Theme.LINE};
            border-radius: 9px;
            padding: 7px 11px;
            font-weight: 700;
        }}
        QPushButton:hover {{
            border-color: {Theme.GREEN};
            background-color: {hover_bg};
        }}
        QPushButton:disabled {{
            color: {Theme.MUTED};
            border-color: rgba(127,127,127,0.18);
            background-color: rgba(127,127,127,0.08);
        }}
        QPushButton#PrimaryButton {{
            background-color: {Theme.GREEN};
            border-color: {Theme.GREEN};
            color: #03140a;
            font-weight: 900;
        }}
        QPushButton#PrimaryButton:hover {{ background-color: {Theme.GREEN_2}; }}
        QPushButton#GhostButton {{
            background-color: {ghost_bg};
            border-color: {Theme.GREEN};
            color: {Theme.GREEN};
        }}
        QPushButton#DangerButton {{
            background-color: rgba(239, 68, 68, 0.12);
            border-color: rgba(239, 68, 68, 0.55);
            color: {Theme.RED};
        }}
        QPushButton#NavButton {{
            background-color: transparent;
            border: 0;
            border-radius: 14px;
            color: {Theme.MUTED};
            padding: 8px 14px;
        }}
        QPushButton#NavButton[active="true"] {{
            background-color: rgba(34, 197, 94, 0.14);
            color: {Theme.GREEN};
            border: 1px solid {Theme.GREEN};
        }}
        QPushButton#AccentButton {{
            background-color: {accent_bg};
            border: 1px solid {Theme.LINE};
            border-radius: 9px;
            padding: 8px 12px;
            font-weight: 850;
        }}
        QPushButton#AccentButton:hover {{ background-color: {ghost_bg}; }}
        QPushButton#DayButton {{
            background: transparent;
            border: 0;
            padding: 2px;
            min-height: 18px;
            font-weight: 800;
        }}
        QPushButton#DayButton[active="true"] {{ color: {Theme.GREEN}; }}
        QLineEdit, QComboBox, QSpinBox {{
            background-color: {input_bg};
            border: 1px solid {Theme.LINE};
            border-radius: 10px;
            padding: 8px 10px;
            color: {Theme.TEXT};
            selection-background-color: {Theme.GREEN};
        }}
        QLineEdit:focus, QComboBox:focus {{ border-color: {Theme.GREEN}; }}
        QComboBox::drop-down {{ border: 0; width: 22px; }}
        QComboBox QAbstractItemView {{
            background-color: {Theme.SURFACE};
            color: {Theme.TEXT};
            border: 1px solid {Theme.LINE};
            selection-background-color: {Theme.GREEN};
            selection-color: #03140a;
            outline: 0;
            padding: 4px;
        }}
        QComboBox QAbstractItemView::item {{
            min-height: 26px;
            padding: 6px 10px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: {hover_bg};
        }}
        QScrollArea {{ border: 0; background: transparent; }}
        QScrollArea#CleanScroll QWidget {{ background: transparent; }}
        QScrollBar:vertical {{
            background: transparent;
            width: 7px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(93, 117, 140, 0.55);
            min-height: 42px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {Theme.GREEN}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QCheckBox {{ color: {Theme.TEXT}; spacing: 8px; }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 5px;
            border: 1px solid {Theme.LINE};
            background: {input_bg};
        }}
        QCheckBox::indicator:checked {{
            background: {Theme.GREEN};
            border-color: {Theme.GREEN};
        }}
        """
