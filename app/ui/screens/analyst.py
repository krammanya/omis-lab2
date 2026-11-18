"""Analytics with a drill-down chart, metrics and JSON export."""
import json
from collections import Counter
from datetime import date
from tkinter import filedialog, messagebox
from ...algorithms import summary
from ..widgets import label, button, choice, metrics, distribution, table


class AnalystScreens:
    def analyst_home(self):
        self.page("Обзор клиентского опыта")
        self.period = choice(self.body, "Период", ["Все", "Текущий месяц"])
        self.product_filter = choice(self.body, "Продукт", ["Все продукты"] + [p.name for p in self.products])
        button(self.body, "Обновить показатели", self.refresh_analytics)
        self.analytics_area()

    def analytics_area(self):
        from tkinter import ttk
        self.analytics_body = ttk.Frame(self.body)
        self.analytics_body.pack(fill="x")
        self.refresh_analytics()

    def selection(self):
        return self.s.reviews.get_reviews(self.in_selection)

    def in_selection(self, review):
        product = self.product_filter.get() == "Все продукты" or self.product_name(review.product_id) == self.product_filter.get()
        period = self.period.get() == "Все" or review.created_at.strftime("%Y-%m") == date.today().strftime("%Y-%m")
        return product and period

    def refresh_analytics(self):
        for child in self.analytics_body.winfo_children():
            child.destroy()
        self.current_reviews = self.selection()
        metrics(self.analytics_body, summary(self.current_reviews))
        self.analytics_charts()

    def analytics_charts(self):
        label(self.analytics_body, "Распределение оценок · нажмите на столбец, чтобы открыть отзывы")
        distribution(self.analytics_body, {n: sum(r.rating == n for r in self.current_reviews) for n in range(1, 6)}, self.chart_detail)
        self.analytics_insights()
        self.analytics_controls()

    def analytics_insights(self):
        self.s.dashboard.show_charts(self.current_reviews)
        for trend in self.s.dashboard.trends(self.current_reviews):
            label(self.analytics_body, f"Тренд: {trend.metric} — {trend.direction.lower()} ({trend.period.lower()})")
        self.correlation_insight()
        label(self.analytics_body, "Сегменты: " + "; ".join(f"{x.name}: {x.criteria}" for x in self.s.analytics.segment_clients(self.current_reviews)))

    def correlation_insight(self):
        value = self.s.dashboard.correlations(self.current_reviews)[0][1]
        label(self.analytics_body, f"Корреляция оценки и рекомендации: {value if value is not None else 'недостаточно вариативных данных'}")
        label(self.analytics_body, "NPS: доля оценок рекомендации 9–10 минус доля 0–6. Не связан напрямую с оценкой покупки 1–5.")

    def analytics_controls(self):
        button(self.analytics_body, "Экспортировать отчёт JSON", self.report)
        button(self.analytics_body, "Запустить опрос клиентов", self.survey)

    def chart_detail(self, rating=None):
        reviews = [r for r in self.current_reviews if rating is None or r.rating == rating]
        self.page("Отзывы с оценкой " + str(rating) if rating else "Отзывы периода")
        table(self.body, [("date", "Дата"), ("rating", "Оценка"), ("text", "Текст")], [(r.id, (r.created_at.strftime("%d.%m"), r.rating, r.text)) for r in reviews], self.inspect_review)
        label(self.body, "Двойной щелчок по отзыву — прочитать текст полностью.")
        button(self.body, "Вернуться к обзору", self.analyst_home)

    def inspect_review(self, review_id):
        review = next(r for r in self.s.reviews.get_reviews() if r.id == review_id)
        messagebox.showinfo("Отзыв", review.text)

    def report(self):
        report = self.s.reports.form_report(self.period.get(), self.selection())
        path = filedialog.asksaveasfilename(defaultextension=".json", initialfile="review-report.json", filetypes=[("JSON", "*.json")])
        if path:
            self.write_report(path, report)

    def write_report(self, path, report):
        try:
            with open(path, "w", encoding="utf-8") as stream:
                json.dump({"id": report.id, "period": report.period, "product": self.product_filter.get(), "metrics": report.metrics}, stream, ensure_ascii=False, indent=2)
        except OSError as error:
            messagebox.showerror("Не удалось сохранить отчёт", str(error))

    def survey(self):
        count = sum(self.invite_product(product) for product in self.products)
        messagebox.showinfo("Опрос запущен", f"Отправлено внутренних приглашений: {count}. Они доступны клиентам в уведомлениях.")

    def invite_product(self, product):
        recipients = [r.client_id for r in self.selection() if r.product_id == product.id]
        return self.s.surveys.launch(product, recipients) if recipients else 0
