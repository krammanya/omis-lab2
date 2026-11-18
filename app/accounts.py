"""Local demonstration accounts and in-process sessions."""
import hashlib
import hmac
import secrets
from .models import Client, Manager, BusinessAnalyst, UserProfile


class AccountService:
    def __init__(self, repository):
        self.repository, self.accounts, self.sessions = repository, {}, {}
        self.register("client@example.com", "demo123", Client(name="Анна"))
        self.register("manager@example.com", "demo123", Manager(name="Мария"))
        self.register("analyst@example.com", "demo123", BusinessAnalyst(name="Алексей"))

    def register(self, email, password, user):
        salt = secrets.token_hex(16)
        user.email = email
        self.accounts[email] = (salt, self.digest(password, salt), user)
        self.repository.save_profile(UserProfile(id=user.id, client_id=user.id))

    def digest(self, password, salt):
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)

    def login(self, email, password):
        record = self.accounts.get(email.strip().casefold())
        if record is None or not hmac.compare_digest(record[1], self.digest(password, record[0])):
            raise ValueError("Неверный email или пароль")
        return self.start_session(record[2])

    def start_session(self, user):
        token = secrets.token_urlsafe(24)
        self.sessions[token] = user
        return token

    def resolve(self, token):
        if token not in self.sessions:
            raise ValueError("Сессия завершена. Войдите снова.")
        return self.sessions[token]

    def logout(self, token):
        self.sessions.pop(token, None)
