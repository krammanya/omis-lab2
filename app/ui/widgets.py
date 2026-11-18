"""Reusable view components with consistent spacing."""
import tkinter as tk
from tkinter import ttk
from .theme import BG, INK, MUTED, ACCENT


def label(parent, text):
    background = "white" if parent.cget("style") == "Card.TFrame" else BG
    tk.Label(parent, text=text, bg=background, fg=INK, font=("Segoe UI", 10), wraplength=820, justify="left").pack(anchor="w", pady=(3, 9))


def button(parent, text, command):
    ttk.Button(parent, text=text, command=command).pack(anchor="w", pady=6)


def entry(parent, title, secret=False):
    label(parent, title)
    value = tk.StringVar()
    ttk.Entry(parent, textvariable=value, show="*" if secret else "").pack(fill="x", pady=(0, 12))
    return value


def choice(parent, title, values):
    label(parent, title)
    value = tk.StringVar(value=values[0])
    ttk.Combobox(parent, textvariable=value, values=values, state="readonly", font=("Segoe UI", 11)).pack(fill="x", pady=(0, 12), ipady=5)
    return value


def text_area(parent, title):
    label(parent, title)
    widget = tk.Text(parent, height=5, wrap="word", font=("Segoe UI", 11), padx=12, pady=12, relief="flat", highlightthickness=1, highlightbackground="#d7deed")
    widget.pack(fill="x", pady=(0, 12))
    return widget


def card(parent):
    frame = ttk.Frame(parent, padding=18, style="Card.TFrame")
    frame.pack(fill="x", pady=(0, 12))
    return frame


def table(parent, columns, rows, action=None):
    tree = ttk.Treeview(parent, columns=[key for key, _ in columns], show="headings", height=min(9, max(3, len(rows))))
    configure_table(tree, columns, rows)
    tree.pack(fill="x", pady=10)
    tree.bind("<Double-1>", lambda event: action(tree.focus()) if action and tree.focus() else None)
    return tree


def configure_table(tree, columns, rows):
    for key, title in columns:
        tree.heading(key, text=title)
        tree.column(key, width=140, minwidth=60)
    for key, values in rows:
        tree.insert("", "end", iid=key, values=values)


def metrics(parent, values):
    row = ttk.Frame(parent)
    row.pack(fill="x", pady=(2, 18))
    for title, value in values.items():
        metric_tile(row, title, "—" if value is None else value)


def metric_tile(row, title, value):
    tile = tk.Frame(row, bg="white", padx=18, pady=16)
    tile.pack(side="left", fill="both", expand=True, padx=(0, 10))
    tk.Label(tile, text=title, bg="white", fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w")
    tk.Label(tile, text=str(value), bg="white", fg=ACCENT, font=("Segoe UI", 24, "bold")).pack(anchor="w")


def distribution(parent, counts, callback=None):
    canvas = tk.Canvas(parent, height=210, bg="white", highlightthickness=0)
    canvas.pack(fill="x", pady=12)
    for index, (name, value) in enumerate(counts.items()):
        draw_bar(canvas, index, str(name), value, max(counts.values(), default=1), callback)
    return canvas


def draw_bar(canvas, index, name, value, maximum, callback):
    x, top = 70 + index * 140, 165 - 125 * value / max(maximum, 1)
    bar = canvas.create_rectangle(x, top, x + 65, 165, fill=ACCENT, outline="")
    canvas.create_text(x + 32, top - 12, text=str(value), fill=INK, font=("Segoe UI", 11, "bold"))
    canvas.create_text(x + 32, 187, text=name, fill=MUTED, font=("Segoe UI", 10))
    canvas.tag_bind(bar, "<Button-1>", lambda event: callback(int(name)) if callback else None)
