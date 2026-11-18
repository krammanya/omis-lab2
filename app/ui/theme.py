"""Shared palette and ttk styles."""
from tkinter import ttk

BG, INK, MUTED, ACCENT = "#f3f5fa", "#17243b", "#64748b", "#3759d7"


def configure(root):
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")
    configure_text(style)
    configure_controls(style)


def configure_text(style):
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=INK, font=("Segoe UI", 10))
    style.configure("Heading.TLabel", font=("Segoe UI", 23, "bold"))
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("Card.TFrame", background="white", relief="flat")


def configure_controls(style):
    style.configure("TButton", background=ACCENT, foreground="white", font=("Segoe UI", 10), padding=(16, 10), borderwidth=0)
    style.map("TButton", background=[("active", "#2945ae")])
    style.configure("TEntry", padding=8, font=("Segoe UI", 10))
    style.configure("Treeview", rowheight=36, font=("Segoe UI", 10), background="white", fieldbackground="white", borderwidth=0)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e7ecfa", padding=8)
