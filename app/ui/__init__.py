"""Окна по макетам на странице 16 PDF."""
import tkinter as tk
from tkinter import ttk, messagebox

root = None
selected = None


def unavailable(reason):
    messagebox.showinfo("Недоступно", reason)


def window(title, size):
    global root
    if root is None:
        root = tk.Tk()
    for child in root.winfo_children():
        child.destroy()
    root.title(title)
    root.geometry(size)
    root.configure(bg="white")
    return root


def header(parent, title):
    tk.Label(parent, text=title, bg="#ededed", anchor="center", font=("Arial", 10, "bold"), relief="groove").pack(fill="x")


def action(parent, text, command, color="#dbe8ff"):
    tk.Button(parent, text=text, command=command, bg=color, relief="solid", bd=1, padx=12, pady=6).pack(side="left", padx=8, pady=8)


def login():
    frame = window("Окно авторизации", "440x300")
    header(frame, "Окно Авторизации")
    tk.Label(frame, text="Email:", bg="white", anchor="w").pack(fill="x", padx=10)
    email = tk.Entry(frame, font=("Arial", 12)); email.pack(fill="x", padx=10, ipady=6)
    tk.Label(frame, text="Пароль:", bg="white", anchor="w").pack(fill="x", padx=10)
    password = tk.Entry(frame, show="*", font=("Arial", 12)); password.pack(fill="x", padx=10, ipady=6)
    tk.Button(frame, text="Войти", bg="#dbe8ff", command=lambda: choose_role(email.get())).pack(fill="x", padx=10, pady=8, ipady=5)
    tk.Checkbutton(frame, text="Запомнить", bg="white").pack(anchor="w", padx=10)
    tk.Label(frame, text="Для просмотра макетов: client или manager в email", bg="white", fg="#666").pack(pady=5)


def choose_role(email):
    if "manager" in email.casefold():
        manager_list()
    elif "client" in email.casefold():
        client_home()
    else:
        unavailable("Авторизация не описана на диаграмме классов. Для просмотра окон укажите client или manager в email.")


def client_home():
    frame = window("Личный кабинет Клиента", "510x430")
    header(frame, "Личный кабинет Клиента")
    header(frame, "Мои отзывы")
    tk.Label(frame, text="Продукт 1", font=("Arial", 17, "bold"), bg="white").pack(anchor="w", padx=12, pady=10)
    tk.Label(frame, text="Оценка: ★★★★★", fg="#dfaa00", bg="white", font=("Arial", 13)).pack(anchor="w", padx=12)
    tk.Label(frame, text="Текст: Самая лучшая покупка в моей жизни", bg="white").pack(anchor="w", padx=12, pady=6)
    tk.Label(frame, text="Состояние: без ответа", bg="white").pack(anchor="w", padx=12)
    tk.Button(frame, text="Оставить новый отзыв", bg="#dcefdc", command=review_form).pack(side="bottom", fill="x", padx=10, pady=10, ipady=8)
    tk.Button(frame, text="Выйти", command=login).pack(side="bottom", anchor="w", padx=10)


def review_form():
    frame = window("Форма нового отзыва", "500x430")
    header(frame, "Форма нового отзыва")
    tk.Label(frame, text="Продукт:", bg="white").pack(anchor="w", padx=15, pady=(12, 0))
    ttk.Combobox(frame, values=["Продукт 1"], state="readonly").pack(fill="x", padx=15)
    tk.Label(frame, text="Оценка:", bg="white").pack(anchor="w", padx=15, pady=(12, 0))
    rating = tk.IntVar(value=5)
    stars = tk.Frame(frame, bg="white"); stars.pack(anchor="w", padx=15)
    for value in range(1, 6):
        tk.Radiobutton(stars, text="★", variable=rating, value=value, bg="white", fg="#dfaa00").pack(side="left")
    tk.Label(frame, text="Текст:", bg="white").pack(anchor="w", padx=15)
    tk.Text(frame, height=5, relief="solid", bd=1).pack(fill="x", padx=15)
    actions = tk.Frame(frame, bg="white"); actions.pack(pady=10)
    action(actions, "Отправить", lambda: unavailable("Сохранение недоступно: интерфейс БД не содержит конкретной реализации хранения."))
    action(actions, "Отмена", client_home, "#f4d4d4")


def manager_list():
    frame = window("Панель Менеджера (Список отзывов)", "1000x420")
    header(frame, "Панель Менеджера (Список отзывов)")
    filters = ttk.Combobox(frame, values=["Все отзывы", "Позитивная", "Негативная"], state="readonly")
    filters.set("Все отзывы"); filters.pack(fill="x", padx=10, pady=5)
    tk.Button(frame, text="Обновить", bg="#dbe8ff", command=lambda: unavailable("Фильтрация не работает: не задан источник сохранённых результатов анализа.")).pack(fill="x", padx=10)
    header(frame, "Таблица отзывов")
    cols = ("id", "date", "product", "client", "rating", "sentiment", "status", "fake", "action")
    table = ttk.Treeview(frame, columns=cols, show="headings", height=5)
    populate_table(table, cols)
    table.pack(fill="both", expand=True, padx=10, pady=5)
    actions = tk.Frame(frame, bg="white"); actions.pack()
    action(actions, "Ответить", lambda: open_review(table))
    action(actions, "Выйти", login)


def populate_table(table, cols):
    names = ("ID", "Дата", "Товар", "Клиент", "Оценка", "Тональность", "Статус", "Фейк", "Действие")
    for key, name in zip(cols, names):
        table.heading(key, text=name); table.column(key, width=105, anchor="center")
    table.insert("", "end", values=("1", "12.05.24", "Телевизор", "Иван И.", "2/5", "Негативная", "Новый", "Нет", "Ответить"))
    table.insert("", "end", values=("2", "12.05.24", "Наушники", "Аноним", "5/5", "Позитивная", "Отвечен", "Нет", "—"))
    table.insert("", "end", values=("3", "12.05.24", "Ноутбук", "Бот", "1/5", "Негативная", "Новый", "Да", "Скрыть"), tags=("fake",))
    table.tag_configure("fake", background="#f4cccc")


def open_review(table):
    if not table.selection():
        return unavailable("Выберите отзыв в таблице.")
    row = table.item(table.selection()[0], "values")
    if row[0] != "1":
        return unavailable("В макете показана карточка ответа только для первого отзыва.")
    reply_window()


def reply_window():
    frame = window("Окно ответа на отзыв", "760x470")
    header(frame, "Окно ответа на отзыв")
    tk.Label(frame, text="Детали отзыва: ID 1, дата 12.05.24, оценка 2/5\nТовар: Телевизор | Клиент: Иван И.", bg="white", justify="left").pack(anchor="w", padx=15, pady=8)
    tk.Label(frame, text="Доставка задержалась на 3 дня, товар хороший, но сервис ужасный!", bg="#f4cccc", anchor="w", padx=10, pady=12).pack(fill="x", padx=15)
    tk.Label(frame, text="Анализ: Тональность — Негативная, Категория — Доставка", bg="white", fg="#b00020").pack(anchor="w", padx=15, pady=10)
    tk.Label(frame, text="Ваш ответ:", bg="white").pack(anchor="w", padx=15)
    tk.Text(frame, height=5, relief="solid", bd=1).pack(fill="x", padx=15)
    actions = tk.Frame(frame, bg="white"); actions.pack(anchor="w", padx=8)
    action(actions, "Сгенерировать ответ ИИ", lambda: unavailable("Генерация недоступна: на базовой диаграмме классов нет метода генерации черновика."), "#e3d7eb")
    action(actions, "Отправить ответ", lambda: unavailable("Ответ не сохраняется: на диаграмме не задана конкретная реализация БД."), "#dcefdc")
    action(actions, "Назад", manager_list)


def run():
    login()
    root.mainloop()
