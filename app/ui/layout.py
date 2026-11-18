"""Window shell with navigation and a scrollable content area."""
import tkinter as tk
from tkinter import ttk
from .widgets import button
from .theme import BG


def clear(root):
    for child in root.winfo_children():
        child.destroy()


def build_shell(app, title):
    clear(app.root)
    sidebar(app)
    frame = ttk.Frame(app.root, padding=(26, 22))
    frame.pack(fill="both", expand=True)
    return content(frame, title)


def sidebar(app):
    rail = tk.Frame(app.root, bg="#152440", width=210, padx=18, pady=28)
    rail.pack(side="left", fill="y")
    rail.pack_propagate(False)
    rail_labels(rail, app)
    rail_actions(rail, app)


def rail_labels(rail, app):
    tk.Label(rail, text="ОТКЛИК", fg="white", bg="#152440", font=("Segoe UI", 23, "bold")).pack(anchor="w")
    tk.Label(rail, text="Клиентский опыт", fg="#aab9d5", bg="#152440", font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 35))
    name = app.user.name if app.user else "Добро пожаловать"
    tk.Label(rail, text=name, fg="white", bg="#152440", font=("Segoe UI", 12), wraplength=175).pack(anchor="w")


def rail_actions(rail, app):
    if app.user:
        button(rail, "Мой кабинет", app.home)
        button(rail, "Уведомления", app.show_notifications)
        button(rail, "Выйти", app.logout)
    tk.Label(rail, text="Лабораторная работа №2", fg="#aab9d5", bg="#152440", font=("Segoe UI", 9)).pack(side="bottom")


def content(frame, title):
    ttk.Label(frame, text=title, style="Heading.TLabel").pack(anchor="w", pady=(0, 20))
    canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    return scrolling_body(canvas, scrollbar)


def scrolling_body(canvas, scrollbar):
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    body = ttk.Frame(canvas)
    bind_body(canvas, body)
    return body


def bind_body(canvas, body):
    item = canvas.create_window((0, 0), window=body, anchor="nw")
    body.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda event: canvas.itemconfigure(item, width=event.width))
    canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-int(event.delta / 120), "units"))
