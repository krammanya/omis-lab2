"""Компоненты интерфейса: auth."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ...models import BusinessAnalyst, Client, Manager, Role


class AuthScreens:

    def show_login(self) -> None:
        self._clear()
        self._header("Добро пожаловать", "Платформа учёта и анализа клиентского опыта и отзывов")
        content = self._content()
        card = self._card(content, 24)
        ttk.Label(card, text="Вход в систему", style="SubTitle.TLabel").pack(anchor="w", pady=(0, 14))
        ttk.Label(card, text="Выберите роль").pack(anchor="w")
        role_var = tk.StringVar(value=Role.CLIENT.value)
        role_row = ttk.Frame(card, style="Card.TFrame")
        role_row.pack(fill="x", pady=(5, 14))
        for role in Role:
            ttk.Radiobutton(role_row, text=role.value, variable=role_var, value=role.value).pack(side="left", padx=(0, 18))
        ttk.Label(card, text="Имя пользователя").pack(anchor="w")
        name = ttk.Entry(card, width=42)
        name.insert(0, "Анна")
        name.pack(anchor="w", pady=(5, 12))
        ttk.Label(card, text="Электронная почта").pack(anchor="w")
        email = ttk.Entry(card, width=42)
        email.insert(0, "user@example.com")
        email.pack(anchor="w", pady=(5, 16))
        ttk.Label(card, text="Пароль").pack(anchor="w")
        password = ttk.Entry(card, width=42, show="*")
        password.pack(anchor="w", pady=(5, 16))
        self._button(card, "Войти", lambda: self._authenticate(role_var.get(), name.get(), email.get(), password.get()), True).pack(anchor="w")
        ttk.Label(content, text="Демонстрационный интерфейс лабораторной работы. Данные хранятся только до закрытия приложения.").pack(anchor="w", pady=(16, 0))

    def _authenticate(self, role: str, name: str, email: str, password: str) -> None:
        if not name.strip() or not email.strip() or not password:
            messagebox.showerror("Ошибка входа", "Заполните имя, адрес электронной почты и пароль.")
            return
        self.role = Role(role)
        key = (self.role, email.strip().casefold())
        if self.role == Role.CLIENT:
            self.user = self.users.setdefault(key, Client(email=email.strip(), name=name.strip()))
            self.show_client_home()
        elif self.role == Role.MANAGER:
            self.user = self.users.setdefault(key, Manager(email=email.strip(), name=name.strip()))
            self.show_manager_home()
        else:
            self.user = self.users.setdefault(key, BusinessAnalyst(email=email.strip(), name=name.strip()))
            self.show_analyst_home()
