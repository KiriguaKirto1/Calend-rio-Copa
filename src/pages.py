from __future__ import annotations

import calendar as pycalendar
from collections import Counter, defaultdict
from typing import Callable

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .data_store import DataStore
from .exporters import export_match_ics
from .icons import icon, icon_size
from .models import Match
from .platform_utils import open_file
from .theme import Theme
from .widgets import FlagBadge, PhaseChip, StadiumPreview, card_layout, hline, label


MONTHS_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            clear_layout(item.layout())


def scrollable(widget: QWidget) -> QScrollArea:
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(widget)
    area.setFrameShape(QFrame.Shape.NoFrame)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    area.setObjectName("CleanScroll")
    return area


def phase_bucket(phase: str) -> tuple[str, str]:
    phase_norm = phase.strip().lower()
    if "grupo" in phase_norm:
        return "Fase de grupos", Theme.BLUE
    if "semi" in phase_norm:
        return "Semifinal", Theme.PURPLE
    if "3º" in phase_norm or "terceiro" in phase_norm or "3rd" in phase_norm or "third" in phase_norm:
        return "3º lugar", Theme.YELLOW
    mata_terms = ("round of 32", "round of 16", "32 avos", "16 avos", "oitavas", "quartas", "quarter", "mata")
    if any(term in phase_norm for term in mata_terms):
        return "Mata-mata", Theme.ORANGE
    if phase_norm == "final" or phase_norm.endswith(" final"):
        return "Final", Theme.RED
    return "Mata-mata", Theme.ORANGE

def concise_phase(phase: str) -> str:
    bucket, _ = phase_bucket(phase)
    if bucket == "Fase de grupos":
        return "Grupos"
    return bucket


def safe_text(text: str, limit: int = 28) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)] + "…"


def current_fuso(store: DataStore) -> str:
    return str(store.preferences.get("fuso_horario", "(GMT-03:00) Brasília"))


def current_date_format(store: DataStore) -> str:
    region = str(store.preferences.get("idioma_regiao", ""))
    if not region:
        region = str(store.preferences.get("idioma", "Português (Brasil)"))
    if region.startswith("English"):
        return "MM/DD/YYYY"
    return "DD/MM/YYYY"


def format_dt(dt, date_format: str = "DD/MM/YYYY", short: bool = False) -> str:
    if date_format == "MM/DD/YYYY":
        return dt.strftime("%m/%d" if short else "%m/%d/%Y")
    return dt.strftime("%d/%m" if short else "%d/%m/%Y")


def display_date(match: Match, store: DataStore, short: bool = False) -> str:
    return format_dt(match.display_kickoff(current_fuso(store)), current_date_format(store), short)


class MiniMatchRow(QFrame):
    details_requested = Signal(str)

    def __init__(self, match: Match, fuso_horario: str = "", date_format: str = "DD/MM/YYYY", parent=None) -> None:
        super().__init__(parent)
        self.match = match
        self.fuso_horario = fuso_horario
        self.date_format = date_format
        self.setObjectName("MatchRow")
        self.setMinimumHeight(Theme.row_height(58, 48))
        self.setMaximumHeight(Theme.row_height(68, 56))
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)

        lay.addWidget(FlagBadge(match.pais_a, match.sigla_a, 34))
        left = QLabel(safe_text(match.time_a, 22))
        left.setStyleSheet("font-weight:800; font-size:13px;")
        lay.addWidget(left, 2)

        mid = QVBoxLayout()
        mid.setSpacing(0)
        time = QLabel(match.display_time(self.fuso_horario))
        time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time.setStyleSheet(f"color:{Theme.GREEN}; font-size:16px; font-weight:900;")
        meta = QLabel(f"{format_dt(match.display_kickoff(self.fuso_horario), self.date_format, short=True)} • {safe_text(match.estadio, 24)}")
        meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        meta.setObjectName("SmallMuted")
        mid.addWidget(time)
        mid.addWidget(meta)
        lay.addLayout(mid, 2)

        right = QLabel(safe_text(match.time_b, 22))
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        right.setStyleSheet("font-weight:800; font-size:13px;")
        lay.addWidget(right, 2)
        lay.addWidget(FlagBadge(match.pais_b, match.sigla_b, 34))
        btn = QPushButton("Detalhes")
        btn.setObjectName("GhostButton")
        btn.setIcon(icon("next", Theme.GREEN, 12))
        btn.setIconSize(icon_size(12))
        btn.clicked.connect(lambda: self.details_requested.emit(match.id))
        lay.addWidget(btn)




class CompactRelatedRow(QFrame):
    details_requested = Signal(str)

    def __init__(self, match: Match, fuso_horario: str = "", date_format: str = "DD/MM/YYYY", parent=None) -> None:
        super().__init__(parent)
        self.match = match
        self.fuso_horario = fuso_horario
        self.date_format = date_format
        self.setObjectName("MatchRow")
        self.setMinimumHeight(Theme.row_height(46, 40))
        self.setMaximumHeight(Theme.row_height(52, 44))
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(8)
        lay.addWidget(FlagBadge(match.pais_a, match.sigla_a, 28))
        lay.addWidget(label(safe_text(match.time_a, 18)), 2)
        mid = QLabel(f"{match.display_time(self.fuso_horario)} · {format_dt(match.display_kickoff(self.fuso_horario), self.date_format, short=True)}")
        mid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mid.setStyleSheet(f"color:{Theme.GREEN}; font-weight:900; font-size:13px;")
        lay.addWidget(mid, 1)
        away = QLabel(safe_text(match.time_b, 18))
        away.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        away.setStyleSheet("font-weight:800;")
        lay.addWidget(away, 2)
        lay.addWidget(FlagBadge(match.pais_b, match.sigla_b, 28))
        btn = QPushButton("Ver")
        btn.setObjectName("GhostButton")
        btn.clicked.connect(lambda: self.details_requested.emit(match.id))
        lay.addWidget(btn)

class DashboardPage(QWidget):
    details_requested = Signal(str)
    page_requested = Signal(str)

    def __init__(self, store: DataStore, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(12)
        self.build()

    def rebuild(self) -> None:
        clear_layout(self.root)
        self.build()

    def build(self) -> None:
        self.root.addWidget(self.hero_header())

        top = QHBoxLayout()
        top.setSpacing(12)
        top.addWidget(self.next_match_card(), 3)
        top.addWidget(self.stats_card(), 2)
        self.root.addLayout(top)

        lower = QHBoxLayout()
        lower.setSpacing(12)
        lower.addWidget(self.upcoming_card(), 3)
        lower.addWidget(self.phases_card(), 2)
        self.root.addLayout(lower, 1)

    def hero_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("HeroCard")
        frame.setMaximumHeight(96)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(18)

        text = QVBoxLayout()
        text.setSpacing(4)
        title = QLabel("Calendário da Copa 2026")
        title.setObjectName("Title")
        subtitle = QLabel("Acompanhe partidas por data, fase e estádio")
        subtitle.setObjectName("Subtitle")
        data_note = QLabel(f"Base carregada: {len(self.store.matches)} partidas • dados locais com validação")
        data_note.setObjectName("SmallMuted")
        text.addWidget(title)
        text.addWidget(subtitle)
        text.addWidget(data_note)
        lay.addLayout(text, 3)

        status = QFrame()
        status.setObjectName("InlineInfo")
        status.setMaximumHeight(74)
        sl = QVBoxLayout(status)
        sl.setContentsMargins(12, 10, 12, 10)
        sl.setSpacing(2)
        fonte = self.store.metadata.get("fonte_principal", "Fonte local")
        sl.addWidget(label(f"Fonte: {fonte}", "SmallMuted"))
        sl.addWidget(label("Mata-mata usa placeholders até definição dos classificados.", "SmallMuted"))
        lay.addWidget(status, 2)
        return frame

    def next_match_card(self) -> QFrame:
        match = self.store.next_match()
        frame = QFrame()
        frame.setObjectName("FeaturedCard")
        frame.setMinimumHeight(174)
        frame.setMaximumHeight(196)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(8)

        top = QHBoxLayout()
        top.addWidget(PhaseChip("PRÓXIMO JOGO", Theme.GREEN))
        top.addStretch()
        top.addWidget(PhaseChip(concise_phase(match.fase), Theme.phase_color(match.fase)))
        lay.addLayout(top)

        row = QHBoxLayout()
        row.setSpacing(14)
        row.addLayout(self.team_summary(match.time_a, match.pais_a, match.sigla_a), 1)

        center = QVBoxLayout()
        center.setSpacing(5)
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        versus = QLabel(f"{safe_text(match.time_a, 18)}  x  {safe_text(match.time_b, 18)}")
        versus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        versus.setStyleSheet("font-size:22px; font-weight:900;")
        info = QLabel(f"{display_date(match, self.store)} • {match.display_time(current_fuso(self.store))}\n{match.estadio}\n{match.city_country}")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setObjectName("SmallMuted")
        center.addWidget(versus)
        center.addWidget(info)
        btn = QPushButton("Ver detalhes")
        btn.setObjectName("PrimaryButton")
        btn.setIcon(icon("next", "#03140a", 13))
        btn.setIconSize(icon_size(13))
        btn.clicked.connect(lambda: self.details_requested.emit(match.id))
        center.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        row.addLayout(center, 3)

        row.addLayout(self.team_summary(match.time_b, match.pais_b, match.sigla_b), 1)
        lay.addLayout(row)
        return frame

    def team_summary(self, name: str, country: str, sigla: str) -> QVBoxLayout:
        box = QVBoxLayout()
        box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.setSpacing(5)
        box.addWidget(FlagBadge(country, sigla, 54), alignment=Qt.AlignmentFlag.AlignCenter)
        team = QLabel(safe_text(name.upper(), 16))
        team.setAlignment(Qt.AlignmentFlag.AlignCenter)
        team.setStyleSheet("font-weight:900; font-size:12px;")
        box.addWidget(team)
        return box

    def stats_card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setMinimumHeight(174)
        frame.setMaximumHeight(196)
        lay = QGridLayout(frame)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)
        total = len(self.store.matches)
        scheduled = sum(1 for m in self.store.matches if m.status.lower() == "agendado")
        finished = sum(1 for m in self.store.matches if m.status.lower() == "encerrado")
        placeholders = sum(1 for m in self.store.matches if m.is_placeholder)
        cards = [
            ("JOGOS TOTAIS", str(total), "partidas", "games", Theme.CYAN),
            ("AGENDADOS", str(scheduled), "a disputar", "calendar", Theme.GREEN),
            ("ENCERRADOS", str(finished), "com placar", "info", Theme.BLUE),
            ("PLACEHOLDERS", str(placeholders), "mata-mata", "filter", Theme.ORANGE),
        ]
        for i, (title, value, caption, icon_name, color) in enumerate(cards):
            tile = self.small_stat(title, value, caption, icon_name, color)
            lay.addWidget(tile, i // 2, i % 2)
        return frame

    def small_stat(self, title: str, value: str, caption: str, icon_name: str, color: str) -> QFrame:
        tile = QFrame()
        tile.setObjectName("SoftCard")
        tile.setMinimumHeight(76)
        tl = QHBoxLayout(tile)
        tl.setContentsMargins(12, 10, 12, 10)
        tl.setSpacing(10)
        ico = QLabel()
        ico.setPixmap(icon(icon_name, color, 20).pixmap(24, 24))
        tl.addWidget(ico)
        txt = QVBoxLayout()
        txt.setSpacing(0)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color:{color}; font-size:10px; font-weight:900; letter-spacing:.6px;")
        val = QLabel(value)
        val.setStyleSheet("font-size:24px; font-weight:900;")
        cap = QLabel(caption)
        cap.setObjectName("SmallMuted")
        txt.addWidget(lbl)
        txt.addWidget(val)
        txt.addWidget(cap)
        tl.addLayout(txt)
        return tile

    def upcoming_card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setMinimumHeight(205)
        lay = card_layout(frame, margins=(16, 14, 16, 14), spacing=8)
        head = QHBoxLayout()
        title = QLabel("PRÓXIMAS PARTIDAS")
        title.setObjectName("SectionTitle")
        head.addWidget(title)
        head.addStretch()
        see = QPushButton("Ver jogos")
        see.setObjectName("GhostButton")
        see.clicked.connect(lambda: self.page_requested.emit("games"))
        head.addWidget(see)
        lay.addLayout(head)
        upcoming = [m for m in self.store.matches if m.status.lower() != "encerrado"][:3]
        for m in upcoming:
            row = MiniMatchRow(m, current_fuso(self.store), current_date_format(self.store))
            row.details_requested.connect(self.details_requested.emit)
            lay.addWidget(row)
        return frame

    def phases_card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setMinimumHeight(205)
        lay = card_layout(frame, margins=(16, 14, 16, 14), spacing=8)
        title = QLabel("FASES DA COMPETIÇÃO")
        title.setObjectName("SectionTitle")
        lay.addWidget(title)
        counts = Counter(phase_bucket(m.fase)[0] for m in self.store.matches)
        grid = QGridLayout()
        grid.setSpacing(8)
        phases = [
            ("Fase de grupos", "12 grupos", Theme.BLUE),
            ("Mata-mata", "32 avos a quartas", Theme.ORANGE),
            ("Semifinal", "2 jogos", Theme.PURPLE),
            ("3º lugar", "disputa final", Theme.YELLOW),
            ("Final", "decisão", Theme.RED),
        ]
        for i, (name, caption, color) in enumerate(phases):
            tile = QFrame()
            tile.setObjectName("PhaseTile")
            tile.setMinimumHeight(56)
            tl = QVBoxLayout(tile)
            tl.setContentsMargins(12, 8, 12, 8)
            tl.setSpacing(1)
            n = QLabel(name)
            n.setStyleSheet(f"color:{color}; font-size:14px; font-weight:900;")
            tl.addWidget(n)
            tl.addWidget(label(f"{counts.get(name, 0)} partidas • {caption}", "SmallMuted"))
            grid.addWidget(tile, i // 2, i % 2)
        lay.addLayout(grid)
        return frame


class GamesPage(QWidget):
    details_requested = Signal(str)

    def __init__(self, store: DataStore, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.search = QLineEdit()
        self.phase_filter = QComboBox()
        self.group_filter = QComboBox()
        self.stadium_filter = QComboBox()
        self.status_filter = QComboBox()
        self.count_label = QLabel()
        self.list_layout = QVBoxLayout()
        self.build()

    def build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        head = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("Jogos")
        title.setObjectName("PageTitle")
        title_box.addWidget(title)
        title_box.addWidget(label("Explore todas as partidas da Copa por data, grupo e estádio", "Subtitle"))
        head.addLayout(title_box)
        head.addStretch()
        self.count_label.setObjectName("Subtitle")
        head.addWidget(self.count_label)
        root.addLayout(head)

        filter_card = QFrame()
        filter_card.setObjectName("Card")
        fl = QHBoxLayout(filter_card)
        fl.setContentsMargins(12, 12, 12, 12)
        fl.setSpacing(9)
        self.search.setPlaceholderText("Buscar por time, estádio ou cidade...")
        self.search.textChanged.connect(self.refresh_list)
        fl.addWidget(self.search, 3)
        combos = [
            (self.phase_filter, "Fase", sorted({concise_phase(m.fase) for m in self.store.matches})),
            (self.group_filter, "Grupo", sorted({m.grupo for m in self.store.matches})),
            (self.stadium_filter, "Estádio", sorted({m.estadio for m in self.store.matches})),
            (self.status_filter, "Status", sorted({m.status for m in self.store.matches})),
        ]
        for combo, name, values in combos:
            combo.addItem(f"{name}: Todos", "")
            for v in values:
                combo.addItem(v, v)
            combo.currentIndexChanged.connect(self.refresh_list)
            fl.addWidget(combo, 1)
        clear = QPushButton("Limpar filtros")
        clear.setObjectName("GhostButton")
        clear.clicked.connect(self.clear_filters)
        fl.addWidget(clear)
        root.addWidget(filter_card)

        container = QWidget()
        table_lay = QVBoxLayout(container)
        table_lay.setContentsMargins(0, 0, 0, 0)
        table_lay.setSpacing(8)
        header = QFrame()
        header.setObjectName("TableHeader")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(14, 8, 14, 8)
        for text, stretch in [
            ("Nº", 0),
            ("PARTIDA", 3),
            ("DATA/HORA", 1),
            ("ESTÁDIO / CIDADE", 2),
            ("FASE", 1),
            ("STATUS", 1),
            ("AÇÃO", 1),
        ]:
            lbl = QLabel(text)
            lbl.setObjectName("SmallMuted")
            if text == "Nº":
                lbl.setFixedWidth(38)
                hl.addWidget(lbl)
            else:
                hl.addWidget(lbl, stretch)
        table_lay.addWidget(header)
        self.list_layout.setSpacing(7)
        table_lay.addLayout(self.list_layout)
        root.addWidget(scrollable(container), 1)
        self.refresh_list()

    def clear_filters(self) -> None:
        self.search.clear()
        for c in (self.phase_filter, self.group_filter, self.stadium_filter, self.status_filter):
            c.setCurrentIndex(0)
        self.refresh_list()

    def filtered_matches(self) -> list[Match]:
        text = self.search.text().strip().lower()
        phase = self.phase_filter.currentData()
        group = self.group_filter.currentData()
        stadium = self.stadium_filter.currentData()
        status = self.status_filter.currentData()
        result = []
        for m in self.store.matches:
            if text and text not in m.searchable_text():
                continue
            if phase and concise_phase(m.fase) != phase:
                continue
            if group and m.grupo != group:
                continue
            if stadium and m.estadio != stadium:
                continue
            if status and m.status != status:
                continue
            result.append(m)
        return result

    def refresh_list(self) -> None:
        clear_layout(self.list_layout)
        matches = self.filtered_matches()
        self.count_label.setText(f"Exibindo {len(matches)} de {len(self.store.matches)} partidas")
        if not matches:
            self.list_layout.addWidget(label("Nenhuma partida encontrada com os filtros atuais.", "Muted"))
        for match in matches:
            self.list_layout.addWidget(GameTableRow(match, self.details_requested.emit, current_fuso(self.store), current_date_format(self.store)))
        self.list_layout.addStretch()


class GameTableRow(QFrame):
    def __init__(self, match: Match, on_details: Callable[[str], None], fuso_horario: str = "", date_format: str = "DD/MM/YYYY", parent=None) -> None:
        super().__init__(parent)
        self.date_format = date_format
        self.setObjectName("MatchRow")
        self.setMinimumHeight(Theme.row_height(62, 50))
        self.setMaximumHeight(Theme.row_height(70, 58))
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(10)

        num = label(str(match.numero), "SmallMuted")
        num.setFixedWidth(38)
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(num)

        teams = QHBoxLayout()
        teams.setSpacing(7)
        teams.addWidget(FlagBadge(match.pais_a, match.sigla_a, 32))
        teams.addWidget(label(safe_text(match.time_a, 18)))
        teams.addWidget(label("vs", "SmallMuted"))
        teams.addWidget(FlagBadge(match.pais_b, match.sigla_b, 32))
        teams.addWidget(label(safe_text(match.time_b, 18)))
        teams.addStretch()
        lay.addLayout(teams, 3)

        dt = label(f"{match.display_time(fuso_horario)}\n{format_dt(match.display_kickoff(fuso_horario), self.date_format)}", "Muted")
        lay.addWidget(dt, 1)
        stadium = label(f"{safe_text(match.estadio, 28)}\n{safe_text(match.city_country, 28)}", "Muted")
        lay.addWidget(stadium, 2)
        lay.addWidget(PhaseChip(concise_phase(match.fase), Theme.phase_color(match.fase)), 1)
        status_color = Theme.GREEN if match.status.lower() == "agendado" else Theme.BLUE
        lay.addWidget(PhaseChip(match.status.capitalize(), status_color), 1)
        btn = QPushButton("Detalhes")
        btn.setObjectName("GhostButton")
        btn.clicked.connect(lambda: on_details(match.id))
        lay.addWidget(btn, 1)


class CalendarPage(QWidget):
    details_requested = Signal(str)

    def __init__(self, store: DataStore, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.year = 2026
        self.month = 6
        self.selected_day = self.store.next_match().kickoff.day
        self.grid = QGridLayout()
        self.day_panel = QVBoxLayout()
        self.month_label = QLabel()
        self.summary_label = QLabel()
        self.day_cells: dict[int, QFrame] = {}
        self.matches_by_day: dict[int, list[Match]] = {}
        self.build()

    def build(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        left = QFrame()
        left.setObjectName("Card")
        ll = card_layout(left, margins=(16, 14, 16, 14), spacing=8)
        head = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Calendário")
        title.setObjectName("PageTitle")
        title_box.addWidget(title)
        title_box.addWidget(label("Acompanhe os jogos por dia e fase da competição", "Subtitle"))
        head.addLayout(title_box)
        head.addStretch()
        self.summary_label.setObjectName("Subtitle")
        head.addWidget(self.summary_label)
        ll.addLayout(head)

        nav = QHBoxLayout()
        prev_btn = QPushButton("‹")
        next_btn = QPushButton("›")
        today_btn = QPushButton("Hoje")
        today_btn.setObjectName("GhostButton")
        self.month_label.setStyleSheet("font-size:20px; font-weight:900;")
        prev_btn.clicked.connect(lambda: self.change_month(-1))
        next_btn.clicked.connect(lambda: self.change_month(1))
        today_btn.clicked.connect(self.go_today)
        nav.addWidget(prev_btn)
        nav.addWidget(next_btn)
        nav.addWidget(self.month_label)
        nav.addStretch()
        nav.addWidget(today_btn)
        ll.addLayout(nav)
        self.grid.setSpacing(5)
        ll.addLayout(self.grid, 1)
        ll.addWidget(label("Cores indicam a fase. Clique em um dia para ver os jogos.", "SmallMuted"))
        root.addWidget(left, 3)

        side = QFrame()
        side.setObjectName("Card")
        sl = card_layout(side, margins=(16, 14, 16, 14), spacing=8)
        day_title = QLabel("Jogos do dia")
        day_title.setObjectName("SectionTitle")
        sl.addWidget(day_title)
        sl.addLayout(self.day_panel, 1)
        sl.addWidget(self.legend_card())
        root.addWidget(side, 1)
        self.refresh_calendar()

    def change_month(self, delta: int) -> None:
        self.month += delta
        if self.month < 1:
            self.month = 12
            self.year -= 1
        elif self.month > 12:
            self.month = 1
            self.year += 1
        self.selected_day = 1
        self.refresh_calendar()

    def go_today(self) -> None:
        next_match = self.store.next_match()
        self.year, self.month, self.selected_day = next_match.kickoff.year, next_match.kickoff.month, next_match.kickoff.day
        self.refresh_calendar()

    def refresh_calendar(self) -> None:
        """Reconstrói a grade apenas quando o mês muda.

        Na V5 a grade inteira era destruída e recriada a cada clique em um dia,
        o que travava perceptivelmente no Windows. Agora o clique só atualiza
        o painel lateral e o estado visual da célula selecionada.
        """
        self.month_label.setText(f"{MONTHS_PT.get(self.month, str(self.month))} {self.year}")
        clear_layout(self.grid)
        self.day_cells.clear()
        self.matches_by_day = defaultdict(list)

        days = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for c, d in enumerate(days):
            l = QLabel(d)
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.setObjectName("SmallMuted")
            self.grid.addWidget(l, 0, c)

        for m in self.store.matches:
            if m.kickoff.year == self.year and m.kickoff.month == self.month:
                self.matches_by_day[m.kickoff.day].append(m)

        month_total = sum(len(v) for v in self.matches_by_day.values())
        self.summary_label.setText(f"{month_total} jogos no mês")

        if self.selected_day not in self.matches_by_day and self.matches_by_day:
            self.selected_day = min(self.matches_by_day)

        cal = pycalendar.Calendar(firstweekday=6)
        for row, week in enumerate(cal.monthdayscalendar(self.year, self.month), start=1):
            for col, day in enumerate(week):
                cell = self.day_cell(day, self.matches_by_day.get(day, []))
                self.grid.addWidget(cell, row, col)
                if day:
                    self.day_cells[day] = cell
        self.refresh_day_panel()

    def set_selected_day_visual(self, old_day: int, new_day: int) -> None:
        for day in (old_day, new_day):
            cell = self.day_cells.get(day)
            if cell is not None:
                selected = day == new_day
                cell.setProperty("selected", "true" if selected else "false")
                for btn in cell.findChildren(QPushButton, "DayButton"):
                    btn.setProperty("active", "true" if selected else "false")
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)
                cell.style().unpolish(cell)
                cell.style().polish(cell)
                cell.update()

    def day_cell(self, day: int, matches: list[Match]) -> QFrame:
        cell = QFrame()
        cell.setObjectName("CalendarDay")
        cell.setProperty("selected", "true" if day == self.selected_day and day else "false")
        cell.setMinimumHeight(Theme.row_height(62, 54))
        cell.mousePressEvent = lambda event, d=day: self.select_day(d) if d else None
        lay = QVBoxLayout(cell)
        lay.setContentsMargins(6, 5, 6, 5)
        lay.setSpacing(3)
        if day == 0:
            cell.setProperty("empty", "true")
            return cell
        top = QPushButton(str(day))
        top.setObjectName("DayButton")
        top.setProperty("active", "true" if day == self.selected_day else "false")
        top.clicked.connect(lambda checked=False, d=day: self.select_day(d))
        lay.addWidget(top)
        if matches:
            bucket, color = phase_bucket(matches[0].fase)
            chip_text = f"{len(matches)} jogo" if len(matches) == 1 else f"{len(matches)} jogos"
            chip = PhaseChip(chip_text, color)
            chip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            lay.addWidget(chip)
        else:
            lay.addStretch()
        cell.style().unpolish(cell)
        cell.style().polish(cell)
        return cell

    def select_day(self, day: int) -> None:
        if not day or day == self.selected_day:
            return
        old_day = self.selected_day
        self.selected_day = day
        self.set_selected_day_visual(old_day, day)
        self.refresh_day_panel()

    def refresh_day_panel(self) -> None:
        clear_layout(self.day_panel)
        day_matches = self.matches_by_day.get(self.selected_day, [])
        self.day_panel.addWidget(label(f"{self.selected_day:02d}/{self.month:02d}/{self.year} • {len(day_matches)} jogo(s)", "Subtitle"))
        if not day_matches:
            self.day_panel.addWidget(label("Nenhum jogo neste dia.", "Muted"))
        for m in day_matches[:4]:
            row = MiniMatchRow(m, current_fuso(self.store), current_date_format(self.store))
            row.details_requested.connect(self.details_requested.emit)
            self.day_panel.addWidget(row)
        if len(day_matches) > 4:
            self.day_panel.addWidget(label(f"+{len(day_matches) - 4} jogos neste dia", "SmallMuted"))
        self.day_panel.addStretch()

    def legend_card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("SoftCard")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)
        lay.addWidget(label("Legenda das fases", "SectionTitle"))
        for name, color in [
            ("Fase de grupos", Theme.BLUE),
            ("Mata-mata", Theme.ORANGE),
            ("Semifinal", Theme.PURPLE),
            ("3º lugar", Theme.YELLOW),
            ("Final", Theme.RED),
        ]:
            row = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; font-size:16px;")
            row.addWidget(dot)
            row.addWidget(label(name, "Muted"))
            row.addStretch()
            lay.addLayout(row)
        return frame


class DetailsPage(QWidget):
    back_requested = Signal()
    changed = Signal()

    def __init__(self, store: DataStore, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.match_id = ""
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(10)

    def show_match(self, match_id: str) -> None:
        self.match_id = match_id
        clear_layout(self.root)
        self.build(self.store.by_id(match_id))

    def build(self, m: Match) -> None:
        head = QHBoxLayout()
        back = QPushButton("Voltar")
        back.setIcon(icon("back", Theme.TEXT, 14))
        back.clicked.connect(self.back_requested.emit)
        head.addWidget(back)
        bread = QLabel("Jogos  ›  Detalhes do jogo")
        bread.setObjectName("Subtitle")
        head.addWidget(bread)
        head.addStretch()
        fav_btn = QPushButton("Remover favorito" if m.favorito else "Favoritar")
        fav_btn.setObjectName("GhostButton")
        fav_btn.setIcon(icon("star", Theme.GREEN, 14))
        fav_btn.clicked.connect(lambda: self.toggle_fav(m.id))
        head.addWidget(fav_btn)

        alerts_enabled = bool(self.store.preferences.get("alertas_jogos", True))
        favorites_only = bool(self.store.preferences.get("favoritos_alerta", False))
        alert_btn = QPushButton("Desativar alerta" if m.alerta else "Ativar alerta")
        alert_btn.setObjectName("GhostButton")
        alert_btn.setIcon(icon("bell", Theme.GREEN, 14))
        if not alerts_enabled:
            alert_btn.setText("Alertas desligados")
            alert_btn.setEnabled(False)
        elif favorites_only and not m.favorito:
            alert_btn.setText("Favorite para alertar")
            alert_btn.setEnabled(False)
        else:
            alert_btn.clicked.connect(lambda: self.toggle_alert(m.id))
        head.addWidget(alert_btn)
        exp = QPushButton("Exportar")
        exp.setObjectName("PrimaryButton")
        exp.setIcon(icon("export", "#03140a", 14))
        exp.clicked.connect(lambda: self.export_one(m))
        head.addWidget(exp)
        self.root.addLayout(head)

        hero = self.hero_match(m)
        self.root.addWidget(hero)

        body = QHBoxLayout()
        body.setSpacing(12)
        body.addWidget(self.info_card(m), 1)
        body.addWidget(self.stadium_card(m), 1)
        body.addWidget(self.source_card(m), 1)
        self.root.addLayout(body)

        lower = QHBoxLayout()
        lower.setSpacing(12)
        lower.addWidget(self.related_card(m), 2)
        lower.addWidget(self.notes_card(m), 1)
        self.root.addLayout(lower, 1)

    def hero_match(self, m: Match) -> QFrame:
        hero = QFrame()
        hero.setObjectName("FeaturedCard")
        hero.setMaximumHeight(166)
        lay = QHBoxLayout(hero)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(16)
        lay.addLayout(self.team_hero(m.time_a, m.pais_a, m.sigla_a), 1)
        center = QVBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.setSpacing(6)
        chips = QHBoxLayout()
        chips.addStretch()
        chips.addWidget(PhaseChip(m.grupo, Theme.phase_color(m.fase)))
        chips.addWidget(PhaseChip(concise_phase(m.fase), Theme.phase_color(m.fase)))
        chips.addStretch()
        center.addLayout(chips)
        vs = QLabel(m.score_text.upper())
        vs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs.setStyleSheet(f"font-size:28px; font-weight:900; color:{Theme.GREEN};")
        data = QLabel(f"{display_date(m, self.store)} • {m.display_time(current_fuso(self.store))}\n{m.estadio}\n{m.city_country}")
        data.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data.setObjectName("Muted")
        center.addWidget(vs)
        center.addWidget(data)
        lay.addLayout(center, 2)
        lay.addLayout(self.team_hero(m.time_b, m.pais_b, m.sigla_b), 1)
        return hero

    def team_hero(self, team: str, country: str, sigla: str) -> QVBoxLayout:
        lay = QVBoxLayout()
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(FlagBadge(country, sigla, 64), alignment=Qt.AlignmentFlag.AlignCenter)
        name = QLabel(safe_text(team, 22))
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setStyleSheet("font-size:20px; font-weight:900;")
        lay.addWidget(name)
        lay.addWidget(label(sigla or "TBD", "SmallMuted"), alignment=Qt.AlignmentFlag.AlignCenter)
        return lay

    def info_card(self, m: Match) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        lay = card_layout(frame, margins=(16, 14, 16, 14), spacing=7)
        lay.addWidget(label("Informações da partida", "SectionTitle"))
        fields = [
            ("Competição", "Copa do Mundo FIFA 2026"),
            ("Fase", m.fase),
            ("Grupo", m.grupo),
            ("Jogo", str(m.numero)),
            ("Data", display_date(m, self.store)),
            ("Horário", f"{m.display_time(current_fuso(self.store))} ({current_fuso(self.store)})"),
            ("Status", m.status.capitalize()),
        ]
        for k, v in fields:
            row = QHBoxLayout()
            row.addWidget(label(k, "Muted"))
            row.addStretch()
            row.addWidget(label(str(v)))
            lay.addLayout(row)
        return frame

    def stadium_card(self, m: Match) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        lay = card_layout(frame, margins=(16, 14, 16, 14), spacing=8)
        lay.addWidget(label("Estádio", "SectionTitle"))
        preview = StadiumPreview(m.estadio, m.city_country, m.stadium_image)
        preview.setMinimumHeight(142)
        preview.setMaximumHeight(152)
        lay.addWidget(preview)
        for k, v in [
            ("Localização", m.city_country),
            ("Capacidade", m.capacidade or "A definir"),
            ("Inauguração", m.inauguracao or "A definir"),
            ("Gramado", m.gramado or "Natural"),
        ]:
            row = QHBoxLayout()
            row.addWidget(label(k, "Muted"))
            row.addStretch()
            row.addWidget(label(v))
            lay.addLayout(row)
        return frame

    def source_card(self, m: Match) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        lay = card_layout(frame, margins=(16, 14, 16, 14), spacing=8)
        lay.addWidget(label("Fonte e validade", "SectionTitle"))
        fields = [
            ("Tipo", m.tipo_dado),
            ("Fonte", m.fonte or "A verificar"),
            ("Fuso", m.timezone),
            ("Exibição", m.horario_exibido),
        ]
        for k, v in fields:
            row = QHBoxLayout()
            row.addWidget(label(k, "Muted"))
            row.addStretch()
            row.addWidget(label(str(v)))
            lay.addLayout(row)
        lay.addWidget(hline())
        message = "Conferir fontes oficiais antes da entrega final."
        if m.is_placeholder:
            message = "Esta partida usa placeholder porque depende de classificação."
        lay.addWidget(label(message, "SmallMuted"))
        return frame

    def related_card(self, m: Match) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setMinimumHeight(185)
        lay = card_layout(frame, margins=(16, 14, 16, 14), spacing=7)
        lay.addWidget(label("Jogos relacionados", "SectionTitle"))
        related = [x for x in self.store.matches if x.id != m.id and (x.grupo == m.grupo or x.fase == m.fase)][:3]
        if not related:
            lay.addWidget(label("Nenhum jogo relacionado encontrado.", "Muted"))
        for item in related:
            row = CompactRelatedRow(item)
            row.details_requested.connect(lambda match_id, self=self: self.show_match(match_id))
            lay.addWidget(row)
        lay.addStretch()
        return frame

    def notes_card(self, m: Match) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        lay = card_layout(frame, margins=(16, 14, 16, 14), spacing=8)
        lay.addWidget(label("Observações", "SectionTitle"))
        lay.addWidget(label(m.destaque or "Partida cadastrada na base local do aplicativo.", "Muted"))
        lay.addWidget(hline())
        lay.addWidget(label("O sistema não fabrica confrontos históricos ou dados não verificados.", "SmallMuted"))
        return frame

    def toggle_fav(self, match_id: str) -> None:
        self.store.toggle_favorite(match_id)
        self.changed.emit()
        self.show_match(match_id)

    def toggle_alert(self, match_id: str) -> None:
        self.store.toggle_alert(match_id)
        self.changed.emit()
        self.show_match(match_id)

    def export_one(self, match: Match) -> None:
        path = export_match_ics(match)
        opened = open_file(path)
        extra = "\n\nO arquivo .ics foi aberto no aplicativo padrão do sistema." if opened else "\n\nNão consegui abrir automaticamente o .ics; abra o arquivo manualmente."
        QMessageBox.information(
            self,
            "Exportado",
            f"Arquivo criado em:\n{path}" + extra + "\n\nNo Windows, o calendário pode pedir confirmação para importar o evento.",
        )


class FavoritesPage(QWidget):
    details_requested = Signal(str)

    def __init__(self, store: DataStore, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(10)
        self.build()

    def rebuild(self) -> None:
        clear_layout(self.root)
        self.build()

    def build(self) -> None:
        top = QHBoxLayout()
        txt = QVBoxLayout()
        txt.addWidget(label("Favoritos", "PageTitle"))
        txt.addWidget(label("Partidas salvas para acompanhar com mais facilidade.", "Subtitle"))
        top.addLayout(txt)
        top.addStretch()
        self.root.addLayout(top)
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        favs = self.store.favorites()
        if not favs:
            empty = QFrame()
            empty.setObjectName("Card")
            el = card_layout(empty)
            el.addWidget(label("Nenhum jogo favoritado ainda.", "SectionTitle"))
            el.addWidget(label("Abra uma partida e clique em Favoritar para salvá-la aqui.", "Subtitle"))
            lay.addWidget(empty)
        for m in favs:
            row = MiniMatchRow(m, current_fuso(self.store), current_date_format(self.store))
            row.details_requested.connect(self.details_requested.emit)
            lay.addWidget(row)
        lay.addStretch()
        self.root.addWidget(scrollable(container), 1)


class SettingsPage(QWidget):
    preferences_changed = Signal()

    def __init__(self, store: DataStore, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.preview_holder: QFrame | None = None
        self.root = QHBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(12)
        self.build()

    def rebuild(self) -> None:
        clear_layout(self.root)
        self.build()

    def schedule_rebuild(self) -> None:
        QTimer.singleShot(0, self.rebuild)

    def build(self) -> None:
        root = self.root

        left_col = QWidget()
        left_root = QVBoxLayout(left_col)
        left_root.setContentsMargins(0, 0, 0, 0)
        left_root.setSpacing(8)
        left_root.addWidget(label("Configurações", "PageTitle"))
        left_root.addWidget(label("Personalize sua experiência no aplicativo", "Subtitle"))

        form = QWidget()
        fl = QVBoxLayout(form)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(10)
        fl.addWidget(self.settings_group("Aparência", [
            ("Tema escuro", "Alterna entre tema escuro e claro", "tema_escuro", self.store.preferences.get("tema", "escuro") == "escuro"),
            ("Visualização compacta", "Reduz altura das linhas e espaçamentos", "visual_compacto", self.store.preferences.get("visual_compacto", False)),
        ]))
        fl.addWidget(self.color_group())
        fl.addWidget(self.settings_group("Notificações", [
            ("Alertas de jogos", "Receba notificações antes das partidas", "alertas_jogos", self.store.preferences.get("alertas_jogos", True)),
            ("Mudanças de horário", "Salva preferência para quando houver importação de dados", "mudancas_horario", self.store.preferences.get("mudancas_horario", True)),
            ("Jogos favoritos", "Permite alerta apenas em partidas favoritadas", "favoritos_alerta", self.store.preferences.get("favoritos_alerta", True)),
        ]))
        fl.addWidget(self.combo_group("Fuso horário", "Fuso horário atual", ["(GMT-03:00) Brasília", "(GMT-04:00) Nova York", "(GMT-06:00) Cidade do México"], self.store.preferences.get("fuso_horario", "(GMT-03:00) Brasília"), "fuso_horario"))
        idioma_selected = self.store.preferences.get("idioma_regiao") or f"{self.store.preferences.get('idioma', 'Português (Brasil)')} — {self.store.preferences.get('formato_data', 'DD/MM/AAAA')}"
        fl.addWidget(self.combo_group("Idioma e região", "Idioma / formato de data", ["Português (Brasil) — DD/MM/AAAA", "English — MM/DD/YYYY", "Español — DD/MM/AAAA"], idioma_selected, "idioma_regiao"))
        fl.addStretch()
        left_root.addWidget(scrollable(form), 1)

        root.addWidget(left_col, 2)
        root.addWidget(self.preview_panel(), 1)

    def settings_group(self, title: str, rows: list[tuple[str, str, str, bool]]) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)
        lay.addWidget(label(title, "SectionTitle"))
        for name, desc, key, checked in rows:
            row = QHBoxLayout()
            txt = QVBoxLayout()
            txt.setSpacing(1)
            txt.addWidget(label(name))
            txt.addWidget(label(desc, "SmallMuted"))
            chk = QCheckBox()
            chk.setChecked(checked)
            chk.stateChanged.connect(lambda state, pref_key=key: self.save_checkbox(pref_key, state))
            row.addLayout(txt)
            row.addStretch()
            row.addWidget(chk)
            lay.addLayout(row)
        return frame

    def save_checkbox(self, key: str, state: int) -> None:
        value = bool(state)
        if key == "tema_escuro":
            self.store.set_preference("tema", "escuro" if value else "claro")
        else:
            self.store.set_preference(key, value)
        self.preferences_changed.emit()

    def color_group(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        cl = QVBoxLayout(frame)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(8)
        cl.addWidget(label("Cor de destaque", "SectionTitle"))
        row = QHBoxLayout()
        row.setSpacing(8)
        current = self.store.preferences.get("cor_destaque", "verde")
        for name, color in [("Verde", Theme.GREEN), ("Azul", Theme.CYAN), ("Roxo", Theme.PURPLE), ("Laranja", Theme.ORANGE), ("Vermelho", Theme.RED)]:
            b = QPushButton(name)
            b.setObjectName("AccentButton")
            selected = name.lower() == current
            b.setProperty("selected", "true" if selected else "false")
            b.setStyleSheet(f"border-color:{color}; color:{color};")
            b.clicked.connect(lambda checked=False, value=name.lower(): self.save_accent(value))
            row.addWidget(b)
        cl.addLayout(row)
        return frame

    def save_accent(self, value: str) -> None:
        self.store.set_preference("cor_destaque", value)
        self.preferences_changed.emit()

    def combo_group(self, title: str, desc: str, values: list[str], selected: str, key: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(7)
        lay.addWidget(label(title, "SectionTitle"))
        lay.addWidget(label(desc, "SmallMuted"))
        combo = QComboBox()
        combo.setView(QListView())
        combo.setMaxVisibleItems(min(6, max(3, len(values))))
        combo.addItems(values)
        if selected in values:
            combo.setCurrentText(selected)
        combo.currentTextChanged.connect(lambda value, pref_key=key: self.save_combo(pref_key, value))
        lay.addWidget(combo)
        return frame

    def save_combo(self, key: str, value: str) -> None:
        self.store.set_preference(key, value)
        if key == "idioma_regiao":
            if value.startswith("English"):
                self.store.set_preference("idioma", "English")
                self.store.set_preference("formato_data", "MM/DD/YYYY")
            elif value.startswith("Español"):
                self.store.set_preference("idioma", "Español")
                self.store.set_preference("formato_data", "DD/MM/AAAA")
            else:
                self.store.set_preference("idioma", "Português (Brasil)")
                self.store.set_preference("formato_data", "DD/MM/AAAA")
        self.preferences_changed.emit()

    def preview_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        lay = card_layout(frame, margins=(16, 14, 16, 14), spacing=10)
        lay.addWidget(label("Prévia", "SectionTitle"))
        m = self.store.next_match()

        preview = QFrame()
        preview.setObjectName("SoftCard")
        preview_lay = QHBoxLayout(preview)
        preview_lay.setContentsMargins(12, 10, 12, 10)
        preview_lay.setSpacing(8)
        preview_lay.addWidget(FlagBadge(m.pais_a, m.sigla_a, 34))
        preview_lay.addWidget(label(safe_text(m.time_a, 16)), 1)
        mid = QLabel(f"{m.display_time(current_fuso(self.store))}\n{display_date(m, self.store, short=True)}")
        mid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mid.setStyleSheet(f"color:{Theme.GREEN}; font-weight:900;")
        preview_lay.addWidget(mid, 1)
        away = QLabel(safe_text(m.time_b, 16))
        away.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        away.setStyleSheet("font-weight:800;")
        preview_lay.addWidget(away, 1)
        preview_lay.addWidget(FlagBadge(m.pais_b, m.sigla_b, 34))
        lay.addWidget(preview)

        stadium = StadiumPreview(m.estadio, m.city_country, m.stadium_image)
        stadium.setMinimumHeight(145)
        stadium.setMaximumHeight(155)
        lay.addWidget(stadium)
        lay.addWidget(label("Resumo das preferências", "SectionTitle"))
        prefs = [
            ("Tema", self.store.preferences.get("tema", "escuro")),
            ("Compacto", "ativado" if self.store.preferences.get("visual_compacto", False) else "desativado"),
            ("Cor", self.store.preferences.get("cor_destaque", "verde")),
            ("Alertas", "ativados" if self.store.preferences.get("alertas_jogos", True) else "desativados"),
            ("Favoritos", "somente favoritos" if self.store.preferences.get("favoritos_alerta", True) else "todos os jogos"),
            ("Fuso", self.store.preferences.get("fuso_horario", "Brasília")),
            ("Idioma", self.store.preferences.get("idioma_regiao", "Português (Brasil)")),
        ]
        for k, v in prefs:
            row = QHBoxLayout()
            row.addWidget(label(k, "Muted"))
            row.addStretch()
            val = QLabel(safe_text(str(v), 34))
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(val)
            lay.addLayout(row)
        lay.addStretch()
        return frame
