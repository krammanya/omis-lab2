"""Manager boundary is used by the list and reply screens."""
from tkinter import messagebox
from ...models import ReviewDraft
from ..widgets import label, button, choice, text_area, metrics, table, card


class ManagerScreens:
    def manager_home(self):
        self.page("Рабочее место менеджера")
        reviews = self.s.panel.open_review_list()
        metrics(self.body, {"Отзывы": len(reviews), "Без ответа": sum(not r.reply_id for r in reviews), "На проверку": sum(r.suspicious for r in reviews)})
        self.manager_filters()
        self.review_list()

    def manager_filters(self):
        self.sentiment = choice(self.body, "Тональность", ["Все", "Позитивная", "Негативная", "Нейтральная"])
        self.status_filter = choice(self.body, "Статус", ["Все", "Без ответа", "На проверку"])
        button(self.body, "Применить фильтры", self.review_list)

    def matches(self, review):
        result = self.s.results.get_result(review.id)
        tone = self.sentiment.get() == "Все" or result.sentiment == self.sentiment.get()
        status = self.status_filter.get() == "Все" or (not review.reply_id if self.status_filter.get() == "Без ответа" else review.suspicious)
        return tone and status

    def review_list(self):
        if hasattr(self, "review_table") and self.review_table.winfo_exists():
            self.review_table.destroy()
        reviews = self.s.panel.open_review_list(self.matches)
        self.review_table = table(self.body, [("date", "Дата"), ("product", "Продукт"), ("rating", "Оценка"), ("tone", "Тональность"), ("status", "Статус")], [(r.id, self.review_row(r)) for r in reviews], self.open_review)
        label(self.body, "Двойной щелчок по строке — открыть отзыв и ответить.")

    def review_row(self, review):
        status = "На проверку" if self.s.panel.show_suspicious_label(review) else "Отвечен" if review.reply_id else "Новый"
        return review.created_at.strftime("%d.%m.%Y"), self.product_name(review.product_id), f"{review.rating}/5", self.s.results.get_result(review.id).sentiment, status

    def open_review(self, review_id):
        self.reply_page(next(r for r in self.s.reviews.get_reviews() if r.id == review_id))

    def reply_page(self, review):
        self.selected = review
        self.draft = next(iter(self.s.reviews.find(lambda x: isinstance(x, ReviewDraft) and x.review_id == review.id)), None)
        self.page("Ответ клиенту")
        self.review_details(review)
        self.reply_controls()

    def review_details(self, review):
        result = self.s.results.get_result(review.id)
        label(self.body, f"{self.product_name(review.product_id)}  ·  {review.rating}/5  ·  {review.created_at:%d.%m.%Y}")
        label(self.body, self.user.read_review(review))
        label(self.body, f"{result.sentiment}  ·  Темы: {', '.join(result.categories)}  ·  Сущности: {', '.join(result.key_entities) or 'не найдены'}")
        label(self.body, f"Оценка доверия по правилам: {review.trust_level:.0%}. " + ("Требуется ручная проверка." if review.suspicious else "Признаков риска не найдено."))

    def reply_controls(self):
        reply = self.s.reviews.get_reply(self.selected.id)
        if reply:
            label(self.body, "Отправленный ответ: " + reply.text)
        else:
            self.reply_editor()

    def reply_editor(self):
        self.reply_text = text_area(self.body, "Ваш ответ")
        self.reply_text.insert("1.0", self.draft.text if self.draft else "")
        button(self.body, "Подготовить черновик по теме отзыва", self.request_draft)
        self.reply_actions()

    def reply_actions(self):
        button(self.body, "Сохранить черновик", self.save_draft)
        button(self.body, "Отправить ответ", lambda: self.guarded(self.send_reply))
        button(self.body, "Назад к отзывам", self.manager_home)

    def request_draft(self):
        self.draft = self.s.panel.request_draft(self.selected, self.s.results.get_result(self.selected.id))
        self.reply_text.delete("1.0", "end")
        self.reply_text.insert("1.0", self.draft.text)

    def save_draft(self):
        self.draft = self.draft or ReviewDraft(review_id=self.selected.id)
        self.s.panel.edit_draft(self.draft, self.reply_text.get("1.0", "end").strip())
        messagebox.showinfo("Черновик сохранён", "Текст доступен при следующем открытии отзыва.")

    def send_reply(self):
        text = self.reply_text.get("1.0", "end").strip()
        if not text:
            raise ValueError("Введите ответ")
        self.s.reply.send(self.user, self.selected, text, self.draft is not None and self.draft.status == "Сгенерирован")
        self.manager_home()
