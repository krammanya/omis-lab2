"""Компоненты интерфейса: analyst."""

from __future__ import annotations

from tkinter import messagebox, ttk

from ...models import Review


class AnalystScreens:

    def show_analyst_home(self) -> None:
        self._clear()
        all_reviews = self.reviews.get_reviews()
        nps = self.metrics.calculate_nps(all_reviews)
        self._header("Аналитическая панель", "Метрики и динамика клиентского опыта")
        content = self._content()
        metrics = ttk.Frame(content)
        metrics.pack(fill="x")
        for name, value in (("Отзывов", len(all_reviews)), ("Средняя оценка", f"{sum(r.rating for r in all_reviews) / len(all_reviews):.1f}/5" if all_reviews else "—"), ("NPS · условно", nps)):
            card = ttk.Frame(metrics, style="Card.TFrame", padding=18)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ttk.Label(card, text=name, style="Card.TLabel").pack(anchor="w")
            ttk.Label(card, text=str(value), style="SubTitle.TLabel").pack(anchor="w", pady=(7, 0))
        card = self._card(content, 18)
        ttk.Label(card, text="Аналитика по продуктам", style="SubTitle.TLabel").pack(anchor="w", pady=(0, 12))
        table = ttk.Treeview(card, columns=("product", "count", "average", "negative"), show="headings", height=6)
        for key, label in (("product", "Продукт"), ("count", "Отзывы"), ("average", "Средняя оценка"), ("negative", "Негативные")):
            table.heading(key, text=label)
            table.column(key, width=180, anchor="w")
        table.pack(fill="x")
        for product in self.products:
            product_reviews = [r for r in all_reviews if r.product_id == product.id]
            negative = sum(self.analysis.analyze(r).sentiment == "Негативная" for r in product_reviews)
            average = f"{sum(r.rating for r in product_reviews) / len(product_reviews):.1f}" if product_reviews else "—"
            table.insert("", "end", values=(product.name, len(product_reviews), average, negative))
        controls = ttk.Frame(content)
        controls.pack(fill="x", pady=8)
        self._button(controls, "Сформировать отчёт", lambda: self._generate_report(all_reviews), True).pack(side="left", padx=(0, 8))
        self._button(controls, "Посмотреть график и отзывы", self.show_chart_detail).pack(side="left")
        self._nav("analyst")

    def _generate_report(self, reviews: list[Review]) -> None:
        report = self.reports.form_report("Текущий период", reviews)
        messagebox.showinfo("Отчёт сформирован", f"Отчёт {report.id[:8]} создан. Отзывов в выборке: {len(reviews)}.")

    def show_chart_detail(self) -> None:
        self._clear()
        self._header("Детализация аналитики", "Распределение отзывов по оценкам")
        content = self._content()
        card = self._card(content)
        reviews = self.reviews.get_reviews()
        counts = {rating: sum(review.rating == rating for review in reviews) for rating in range(1, 6)}
        ttk.Label(card, text=f"NPS: {self.metrics.calculate_nps(reviews)} · Всего отзывов: {len(reviews)}", style="SubTitle.TLabel").pack(anchor="w", pady=(0, 12))
        for rating, count in counts.items():
            row = ttk.Frame(card, style="Card.TFrame")
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=f"{rating} из 5", style="Card.TLabel", width=10).pack(side="left")
            bar = ttk.Progressbar(row, maximum=max(len(reviews), 1), value=count, length=420)
            bar.pack(side="left", padx=8)
            ttk.Label(row, text=str(count), style="Card.TLabel").pack(side="left")
        ttk.Label(card, text="Отзывы", style="SubTitle.TLabel").pack(anchor="w", pady=(15, 5))
        for review in reviews:
            ttk.Label(card, text=f"{review.rating}/5 — {review.text}", style="Card.TLabel", wraplength=800).pack(anchor="w")
        ttk.Label(card, text="Нажмите «Вернуться», чтобы открыть сводную панель.", style="Card.TLabel").pack(anchor="w", pady=(14, 0))
        self._button(content, "Вернуться к панели", self.show_analyst_home).pack(anchor="w")
        self._nav("analyst")
