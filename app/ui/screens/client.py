"""Client cabinet, review form, and answer history."""
import tkinter as tk
from ...models import Review
from ..widgets import label, button, choice, text_area, card, metrics


class ClientScreens:
    def client_home(self):
        self.page("Мои отзывы")
        reviews = self.user.view_history(self.s.reviews.get_reviews())
        metrics(self.body, {"Всего отзывов": len(reviews), "Получено ответов": sum(bool(r.reply_id) for r in reviews)})
        button(self.body, "+ Оставить отзыв", self.review_form)
        self.history_cards(reviews)

    def history_cards(self, reviews):
        if not reviews:
            label(self.body, "У вас пока нет отзывов. Расскажите о первой покупке.")
        for review in reversed(reviews):
            self.review_summary(review)

    def review_summary(self, review):
        frame = card(self.body)
        label(frame, f"{self.product_name(review.product_id)}  ·  {'★' * review.rating}  ·  {review.created_at:%d.%m.%Y}")
        label(frame, review.text)
        reply = self.s.reviews.get_reply(review.id)
        label(frame, "Ответ команды: " + reply.text if reply else "Ожидает ответа команды")

    def review_form(self):
        self.page("Оставить отзыв")
        self.form_product = choice(self.body, "Какой продукт вы оцениваете?", [p.name for p in self.products])
        self.rating = choice(self.body, "Оценка покупки · 1–5", ["5", "4", "3", "2", "1"])
        self.recommendation = choice(self.body, "Насколько вероятно, что вы порекомендуете нас? · 0–10", ["Не отвечать"] + [str(n) for n in range(11)])
        self.review_fields()

    def review_fields(self):
        self.review_text = text_area(self.body, "Что понравилось или что стоит улучшить?")
        self.anonymous = tk.BooleanVar()
        tk.Checkbutton(self.body, text="Не показывать моё имя менеджеру", variable=self.anonymous, bg="#f3f5fa").pack(anchor="w")
        button(self.body, "Отправить отзыв", lambda: self.guarded(self.submit_review))
        button(self.body, "Отмена", self.client_home)

    def make_review(self):
        product = next(p for p in self.products if p.name == self.form_product.get())
        score = None if self.recommendation.get() == "Не отвечать" else int(self.recommendation.get())
        return Review(text=self.review_text.get("1.0", "end").strip(), rating=int(self.rating.get()),
                      recommendation=score, anonymous=self.anonymous.get(), client_id=self.user.id,
                      product_id=product.id, company_id=self.company.id)

    def submit_review(self):
        review = self.make_review()
        if not review.text:
            raise ValueError("Напишите несколько слов о покупке")
        self.s.submit.submit(review)
        self.client_home()
