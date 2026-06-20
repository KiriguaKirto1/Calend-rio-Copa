from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QWidget

from .data_store import DataStore
from .exporters import export_all_ics, export_csv
from .icons import app_icon
from .platform_utils import open_file
from .pages import CalendarPage, DashboardPage, DetailsPage, FavoritesPage, GamesPage, SettingsPage
from .theme import Theme
from .widgets import AppBackground, BottomNav, HeaderBar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.store = DataStore()
        Theme.apply_preferences(self.store.preferences)
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(Theme.global_qss())
        self.current_page_name = "dashboard"
        self.setWindowTitle("Calendário da Copa 2026")
        self.setWindowIcon(app_icon())
        self.resize(1280, 720)
        self.setMinimumSize(1040, 640)

        root = AppBackground()
        root.setObjectName("Root")
        self.setCentralWidget(root)
        shell = QVBoxLayout(root)
        shell.setContentsMargins(18, 14, 18, 18)
        shell.setSpacing(14)

        self.header = HeaderBar()
        self.header.export_requested.connect(self.export_all)
        self.header.refresh_requested.connect(self.reload_local_data)
        shell.addWidget(self.header)

        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(self.store)
        self.games_page = GamesPage(self.store)
        self.calendar_page = CalendarPage(self.store)
        self.favorites_page = FavoritesPage(self.store)
        self.details_page = DetailsPage(self.store)
        self.settings_page = SettingsPage(self.store)

        self.pages = {
            "dashboard": self.dashboard_page,
            "games": self.games_page,
            "calendar": self.calendar_page,
            "favorites": self.favorites_page,
            "details": self.details_page,
            "settings": self.settings_page,
        }
        for page in self.pages.values():
            self.stack.addWidget(page)
        shell.addWidget(self.stack, 1)

        self.nav = BottomNav()
        self.nav.page_requested.connect(self.open_page)
        shell.addWidget(self.nav)

        self.dashboard_page.details_requested.connect(self.open_details)
        self.dashboard_page.page_requested.connect(self.open_page)
        self.games_page.details_requested.connect(self.open_details)
        self.calendar_page.details_requested.connect(self.open_details)
        self.favorites_page.details_requested.connect(self.open_details)
        self.details_page.back_requested.connect(lambda: self.open_page("games"))
        self.details_page.changed.connect(self.refresh_dynamic_pages)
        self.settings_page.preferences_changed.connect(self.apply_preference_changes)

        self.open_page("dashboard")

    def open_page(self, page_name: str) -> None:
        if page_name == "settings":
            self.current_page_name = "settings"
            self.stack.setCurrentWidget(self.settings_page)
            self.nav.set_active("settings")
            return
        widget = self.pages.get(page_name)
        if widget is None:
            return
        if page_name == "favorites":
            self.favorites_page.rebuild()
        elif page_name == "dashboard":
            self.dashboard_page.rebuild()
        self.current_page_name = page_name
        self.stack.setCurrentWidget(widget)
        self.nav.set_active(page_name if page_name in self.nav.buttons else "settings")

    def open_details(self, match_id: str) -> None:
        self.current_page_name = "details"
        self.details_page.show_match(match_id)
        self.stack.setCurrentWidget(self.details_page)
        self.nav.set_active("games")

    def refresh_dynamic_pages(self) -> None:
        self.dashboard_page.rebuild()
        self.favorites_page.rebuild()

    def apply_preference_changes(self) -> None:
        """Aplica preferências com o menor recarregamento possível.

        A versão anterior reconstruía todas as páginas a cada clique em
        Configurações. Isso deixava o app travando por alguns instantes. Agora
        a atualização fica restrita à página visível e ao stylesheet global.
        """
        Theme.apply_preferences(self.store.preferences)
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(Theme.global_qss())
        self.centralWidget().update()

        if self.current_page_name == "dashboard":
            self.dashboard_page.rebuild()
        elif self.current_page_name == "games":
            self.games_page.refresh_list()
        elif self.current_page_name == "calendar":
            self.calendar_page.refresh_calendar()
        elif self.current_page_name == "favorites":
            self.favorites_page.rebuild()
        elif self.current_page_name == "details" and self.details_page.match_id:
            self.details_page.show_match(self.details_page.match_id)
        # Em Configurações, manter a tela atual evita lag e não fecha combos/dropdowns.

        self.nav.set_active("games" if self.current_page_name == "details" else self.current_page_name)

    def reload_local_data(self) -> None:
        """Recarrega os JSON locais sem fingir atualização online em tempo real."""
        self.store.load()
        self.dashboard_page.rebuild()
        self.games_page.refresh_list()
        self.calendar_page.refresh_calendar()
        self.favorites_page.rebuild()
        if self.current_page_name == "details" and self.details_page.match_id:
            self.details_page.show_match(self.details_page.match_id)
        QMessageBox.information(
            self,
            "Dados recarregados",
            f"Dados locais recarregados de data/dados_copa.json.\nPartidas carregadas: {len(self.store.matches)}.\n\n"
            "Isto não é atualização em tempo real pela internet.",
        )

    def export_all(self) -> None:
        ics_path = export_all_ics(self.store.matches)
        csv_path = export_csv(self.store.matches)
        opened = open_file(ics_path)
        extra = "\n\nO arquivo .ics foi aberto no aplicativo padrão do sistema." if opened else "\n\nNão consegui abrir automaticamente o .ics; abra o arquivo manualmente."
        QMessageBox.information(
            self,
            "Exportação concluída",
            f"Arquivos criados:\n{ics_path}\n{csv_path}" + extra + "\n\nNo Windows, o calendário pode pedir confirmação para importar os eventos.",
        )
