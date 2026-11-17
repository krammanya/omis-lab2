"""Окно приложения, зависимости и запуск интерфейса."""

from __future__ import annotations

import tkinter as tk

from ..models import BusinessAnalyst, Client, Manager, Product, Role
from ..services import (
    AnalysisModule, InMemoryStorage, MetricsModule, Notification,
    ReportModule, ReviewRepository, TaskQueue, TextGenerator,
)
from .common import CommonUI
from .screens.auth import AuthScreens
from .screens.client import ClientScreens
from .screens.manager import ManagerScreens
from .screens.analyst import AnalystScreens


class ReviewPlatformApp(CommonUI, AuthScreens, ClientScreens, ManagerScreens, AnalystScreens):
    """Окно и общее состояние экранов приложения."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Платформа учёта и анализа клиентского опыта")
        self.root.geometry("1020x700")
        self.root.minsize(860, 600)
        self.root.configure(bg="#f3f5f8")
        self.storage = InMemoryStorage()
        self.reviews = ReviewRepository(self.storage)
        self.analysis = AnalysisModule()
        self.metrics = MetricsModule()
        self.reports = ReportModule()
        self.notifications = Notification()
        self.text_generator = TextGenerator()
        self.tasks = TaskQueue()
        self.user: Client | Manager | BusinessAnalyst | None = None
        self.users: dict[tuple[Role, str], Client | Manager | BusinessAnalyst] = {}
        self.role: Role | None = None
        self.products = [Product(name="Смартфон X"), Product(name="Наушники Pro"), Product(name="Кофемашина 2")]
        self._configure_style()
        self.show_login()

    def run(self) -> None:
        self.root.mainloop()
