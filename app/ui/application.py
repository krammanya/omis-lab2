"""Application lifetime and screen navigation."""
import tkinter as tk
from tkinter import ttk, messagebox
from ..container import create_services, create_catalog
from .screens.auth import AuthScreens
from .screens.client import ClientScreens
from .screens.manager import ManagerScreens
from .screens.analyst import AnalystScreens
from .widgets import label, button
from .theme import configure
from .layout import build_shell
from ..demo import seed
from ..models import Product


class ReviewPlatformApp(AuthScreens, ClientScreens, ManagerScreens, AnalystScreens):
    def __init__(self):
        self.s = create_services()
        self.company, self.product = create_catalog(self.s.storage)
        self.initialize_data()
        self.create_window()
        self.loading()

    def create_window(self):
        self.root = tk.Tk()
        self.root.title("Платформа учёта и анализа отзывов")
        self.root.geometry("1180x820")
        self.finish_window()

    def finish_window(self):
        self.root.minsize(980, 680)
        configure(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def run(self):
        self.root.mainloop()

    def page(self, title):
        self.body = build_shell(self, title)

    def initialize_data(self):
        self.accounts, self.user, self.role, self.token = {}, None, None, None
        self.products = [self.product, Product(name="Наушники Pro", company_id=self.company.id), Product(name="Кофемашина Mini", company_id=self.company.id)]
        self.product.name = "Смартфон X"
        seed(self.s, self.products)

    def product_name(self, product_id):
        return next((item.name for item in self.products if item.id == product_id), "Продукт")

    def show_notifications(self):
        messages = [text for recipient, text in self.s.notifications.messages if recipient in (self.user.id, "manager" if self.role == "Менеджер" else "")]
        self.page("Уведомления")
        for text in messages:
            label(self.body, text)

    def loading(self):
        self.page("Загрузка компонентов… Соединение: локальное хранилище")
        self.root.after(300, self.show_login)

    def navigation(self):
        self.root.update_idletasks()

    def home(self):
        {"Клиент": self.client_home, "Менеджер": self.manager_home,
         "Бизнес-аналитик": self.analyst_home}[self.role]()

    def logout(self):
        self.s.auth.logout(self.token)
        self.user = None
        self.page("До свидания! Сессия завершена.")
        button(self.body, "Закрыть", self.root.destroy)
        button(self.body, "Войти снова", self.show_login)

    def guarded(self, action):
        try:
            action()
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error))
