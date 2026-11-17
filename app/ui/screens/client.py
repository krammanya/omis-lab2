"""Компоненты интерфейса: client."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ...models import ManagerReply, Review


class ClientScreens:

    def show_client_home(self) -> None:
        self._clear()
        self._header("Личный кабинет клиента", "Оставляйте отзывы и просматривайте историю")
        content = self._content()
        self._card(content)
        card = content.winfo_children()[0]
        ttk.Label(card, text="Что вы хотите сделать?", style="SubTitle.TLabel").pack(anchor="w", pady=(0, 14))
        self._button(card, "Оставить отзыв", self.show_review_form, True).pack(anchor="w", pady=4)
        self._button(card, "История моих отзывов", self.show_client_history).pack(anchor="w", pady=4)
        self._nav("client")

    def show_review_form(self) -> None:
        self._clear()
        self._header("Новый отзыв", "Расскажите о своём опыте использования продукта")
        content = self._content()
        card = self._card(content)
        ttk.Label(card, text="Продукт").pack(anchor="w")
        product_var = tk.StringVar(value=self.products[0].name)
        ttk.Combobox(card, textvariable=product_var, values=[p.name for p in self.products], state="readonly", width=48).pack(anchor="w", pady=(5, 12))
        ttk.Label(card, text="Оценка").pack(anchor="w")
        rating = tk.IntVar(value=5)
        ttk.Spinbox(card, from_=1, to=5, textvariable=rating, width=8).pack(anchor="w", pady=(5, 12))
        ttk.Label(card, text="Текст отзыва").pack(anchor="w")
        body = tk.Text(card, height=7, width=76, wrap="word", font=("Segoe UI", 10))
        body.pack(fill="x", pady=(5, 12))
        anonymous = tk.BooleanVar()
        ttk.Checkbutton(card, text="Оставить отзыв анонимно", variable=anonymous).pack(anchor="w", pady=(0, 12))
        self._button(card, "Отправить отзыв", lambda: self._submit_review(product_var.get(), rating.get(), body.get("1.0", "end").strip(), anonymous.get()), True).pack(side="left")
        self._button(card, "Назад", self.show_client_home).pack(side="left", padx=8)
        self._nav("client")

    def _submit_review(self, product_name: str, rating: int, text: str, anonymous: bool) -> None:
        if not text:
            messagebox.showerror("Не отправлено", "Введите текст отзыва.")
            return
        product = next(item for item in self.products if item.name == product_name)
        review = Review(text=text, rating=int(rating), anonymous=anonymous, client_id=self.user.id, product_id=product.id)
        self.user.leave_review(review)
        self.reviews.save_review(review)
        self.tasks.add_task(f"analysis:{review.id}")
        self.analysis.analyze(review)
        messagebox.showinfo("Отзыв отправлен", "Спасибо! Отзыв добавлен в историю.")
        self.show_client_history()

    def show_client_history(self) -> None:
        self._clear()
        self._header("История отзывов", "Ваши отзывы и статусы обработки")
        content = self._content()
        table = ttk.Treeview(content, columns=("date", "product", "rating", "status"), show="headings")
        for key, label, width in (("date", "Дата", 130), ("product", "Продукт", 240), ("rating", "Оценка", 100), ("status", "Статус", 180)):
            table.heading(key, text=label)
            table.column(key, width=width, anchor="w")
        table.pack(fill="both", expand=True)
        own = self.user.view_history(self.reviews.get_reviews())
        for review in own:
            product = next((p.name for p in self.products if p.id == review.product_id), "Продукт")
            table.insert("", "end", iid=review.id, values=(review.created_at.strftime("%d.%m.%Y"), product, f"{review.rating}/5", "Есть ответ" if review.reply_id else "Ожидает ответа"))
        def show_reply() -> None:
            selected = table.selection()
            if not selected:
                messagebox.showinfo("Ответ", "Выберите отзыв.")
                return
            reply = next((item for item in self.storage.find_all(ManagerReply) if item.review_id == selected[0]), None)
            messagebox.showinfo("Ответ менеджера", reply.text if reply else "Ответ пока не получен.")
        self._button(content, "Прочитать ответ", show_reply).pack(anchor="w", pady=(10, 0))
        self._button(content, "Оставить ещё один отзыв", self.show_review_form, True).pack(anchor="w", pady=12)
        self._nav("client")
