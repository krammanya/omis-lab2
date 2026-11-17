"""Компоненты интерфейса: common."""

from __future__ import annotations

from tkinter import ttk

from ..models import Role


class CommonUI:

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f3f5f8")
        style.configure("Card.TFrame", background="white")
        style.configure("TLabel", background="#f3f5f8", foreground="#1e293b", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground="#172554")
        style.configure("SubTitle.TLabel", font=("Segoe UI", 13, "bold"), foreground="#1e293b")
        style.configure("Card.TLabel", background="white", foreground="#334155")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.configure("TButton", padding=(10, 7))
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _clear(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

    def _header(self, title: str, subtitle: str = "") -> ttk.Frame:
        header = ttk.Frame(self.root, padding=(28, 22, 28, 12))
        header.pack(fill="x")
        ttk.Label(header, text=title, style="Title.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(header, text=subtitle).pack(anchor="w", pady=(5, 0))
        return header

    def _content(self) -> ttk.Frame:
        frame = ttk.Frame(self.root, padding=(28, 8, 28, 28))
        frame.pack(fill="both", expand=True)
        return frame

    def _card(self, parent: ttk.Frame, padding: int = 18) -> ttk.Frame:
        card = ttk.Frame(parent, style="Card.TFrame", padding=padding)
        card.pack(fill="x", pady=8)
        return card

    def _button(self, parent: ttk.Frame, text: str, command, primary: bool = False) -> ttk.Button:
        return ttk.Button(parent, text=text, command=command, style="Primary.TButton" if primary else "TButton")

    def _nav(self, active: str) -> ttk.Frame:
        nav = ttk.Frame(self.root, padding=(24, 8, 24, 10))
        nav.pack(fill="x", side="bottom")
        for label, callback in (("Главная", self.show_home), ("Выйти", self.logout)):
            self._button(nav, label, callback).pack(side="left", padx=(0, 8))
        ttk.Label(nav, text=f"{self.user.name if self.user else ''} · {self.role.value if self.role else ''}").pack(side="right")
        return nav

    def show_home(self) -> None:
        if self.role == Role.CLIENT:
            self.show_client_home()
        elif self.role == Role.MANAGER:
            self.show_manager_home()
        elif self.role == Role.ANALYST:
            self.show_analyst_home()
        else:
            self.show_login()

    def logout(self) -> None:
        self.user = None
        self.role = None
        self.show_login()
