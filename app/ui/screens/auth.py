"""Sign-in uses local account validation and a session token."""
from ...models import Client, Manager
from ..widgets import label, button, entry, card


class AuthScreens:
    def show_login(self):
        self.page("Войдите в систему")
        label(self.body, "Отзывы клиентов, ответы команды и аналитика — в одном месте.")
        self.login_fields()
        self.demo_accounts()

    def login_fields(self):
        frame = card(self.body)
        self.email = entry(frame, "Электронная почта")
        self.password = entry(frame, "Пароль", True)
        button(frame, "Войти", lambda: self.guarded(self.authenticate))

    def demo_accounts(self):
        label(self.body, "Тестовые аккаунты · пароль у всех: demo123")
        for caption, email in [("Клиент", "client@example.com"), ("Менеджер", "manager@example.com"), ("Аналитик", "analyst@example.com")]:
            button(self.body, caption + " · " + email, lambda value=email: self.fill_account(value))
        label(self.body, "Демонстрационные данные хранятся до закрытия приложения.")

    def fill_account(self, email):
        self.email.set(email)
        self.password.set("demo123")

    def authenticate(self):
        self.token = self.s.auth.login(self.email.get(), self.password.get())
        self.page("Проверка сессии…")
        self.root.after(100, self.resolve_role)

    def resolve_role(self):
        self.user = self.s.auth.resolve(self.token)
        self.role = "Клиент" if isinstance(self.user, Client) else "Менеджер" if isinstance(self.user, Manager) else "Бизнес-аналитик"
        self.home()
