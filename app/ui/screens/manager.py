"""Компоненты интерфейса: manager."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ...models import Review, ReviewDraft


class ManagerScreens:

    def show_manager_home(self) -> None:
        self._clear()
        self._header("Рабочее место менеджера", "Новые отзывы, анализ и ответы клиентам")
        content = self._content()
        self._card(content)
        card = content.winfo_children()[0]
        all_reviews = self.reviews.get_reviews()
        ttk.Label(card, text=f"Всего отзывов: {len(all_reviews)}", style="SubTitle.TLabel").pack(anchor="w")
        self._button(card, "Открыть список отзывов", self.show_manager_reviews, True).pack(anchor="w", pady=(14, 4))
        if all_reviews:
            ttk.Label(card, text=self.notifications.send(self.user, all_reviews[-1]), style="Card.TLabel").pack(anchor="w", pady=(12, 0))
        self._nav("manager")

    def show_manager_reviews(self) -> None:
        self._clear()
        self._header("Отзывы клиентов", "Выберите отзыв для просмотра анализа и ответа")
        content = self._content()
        table = ttk.Treeview(content, columns=("date", "product", "rating", "sentiment", "text"), show="headings")
        for key, label, width in (("date", "Дата", 110), ("product", "Продукт", 170), ("rating", "Оценка", 80), ("sentiment", "Тональность", 120), ("text", "Текст", 430)):
            table.heading(key, text=label)
            table.column(key, width=width, anchor="w")
        table.pack(fill="both", expand=True)
        reviews = self.reviews.get_reviews()
        for review in reviews:
            result = self.analysis.analyze(review)
            product = next((p.name for p in self.products if p.id == review.product_id), "Продукт")
            table.insert("", "end", iid=review.id, values=(review.created_at.strftime("%d.%m.%Y"), product, f"{review.rating}/5", result.sentiment, review.text[:75]))
        self._button(content, "Открыть выбранный отзыв", lambda: self._open_selected_review(table), True).pack(anchor="w", pady=12)
        self._nav("manager")

    def _open_selected_review(self, table: ttk.Treeview) -> None:
        selected = table.selection()
        if not selected:
            messagebox.showinfo("Выберите отзыв", "Сначала выберите строку в таблице.")
            return
        review = next(item for item in self.reviews.get_reviews() if item.id == selected[0])
        self.show_review_detail(review)

    def show_review_detail(self, review: Review) -> None:
        self._clear()
        result = self.analysis.analyze(review)
        product = next((p.name for p in self.products if p.id == review.product_id), "Продукт")
        self._header("Карточка отзыва", f"{product} · {review.created_at.strftime('%d.%m.%Y')}")
        content = self._content()
        card = self._card(content)
        ttk.Label(card, text=f"Оценка: {review.rating}/5 · Тональность: {result.sentiment}", style="SubTitle.TLabel").pack(anchor="w")
        ttk.Label(card, text=review.text, style="Card.TLabel", wraplength=850, justify="left").pack(anchor="w", pady=(14, 10))
        ttk.Label(card, text=f"Категории: {', '.join(result.categories) or 'не определены'}", style="Card.TLabel").pack(anchor="w", pady=(0, 14))
        ttk.Label(card, text="Ответ клиенту").pack(anchor="w")
        reply = tk.Text(card, height=5, width=90, wrap="word", font=("Segoe UI", 10))
        reply.pack(fill="x", pady=(5, 10))
        draft = next((item for item in self.storage.find_all(ReviewDraft) if item.review_id == review.id), None)
        if draft:
            reply.insert("1.0", draft.text)
        else:
            reply.insert("1.0", self.text_generator.generate_reply(review, result.sentiment))
        actions = ttk.Frame(card, style="Card.TFrame")
        actions.pack(anchor="w")
        self._button(actions, "Сохранить черновик", lambda: self._save_draft(review, reply.get("1.0", "end").strip()), True).pack(side="left", padx=(0, 8))
        self._button(actions, "Отправить ответ", lambda: self._send_reply(review, reply.get("1.0", "end").strip())).pack(side="left")
        self._button(card, "Назад к списку", self.show_manager_reviews).pack(anchor="w", pady=(14, 0))
        self._nav("manager")

    def _save_draft(self, review: Review, text: str) -> None:
        current = next((item for item in self.storage.find_all(ReviewDraft) if item.review_id == review.id), None)
        if current:
            current.text = text
        else:
            self.reviews.save_draft(ReviewDraft(review_id=review.id, text=text))
        messagebox.showinfo("Черновик", "Черновик ответа сохранён.")

    def _send_reply(self, review: Review, text: str) -> None:
        if not text:
            messagebox.showerror("Ответ не отправлен", "Введите текст ответа.")
            return
        reply = self.user.write_reply(review, text)
        self.reviews.save_reply(reply)
        review.reply_id = reply.id
        messagebox.showinfo("Ответ отправлен", "Ответ сохранён в системе.")
        self.show_manager_reviews()
