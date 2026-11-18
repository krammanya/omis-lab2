"""Collaborators from UML. Local implementations of UML collaborators."""
from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque, Counter
from datetime import datetime
from .algorithms import tokens, sentiment_score, CATEGORIES, ENTITIES, pearson, nps, summary
from .models import (AnalysisResult, Review, ManagerReply, ReviewDraft, UserProfile,
                     Report, Trend, CustomerSegment, ActivityHistory, Chart, Metric)


class StorageDB(ABC):
    @abstractmethod
    def save(self, entity): ...

    @abstractmethod
    def find(self, criteria): ...


class InMemoryStorage(StorageDB):
    def __init__(self):
        self.items = []

    def save(self, entity):
        if not any(item is entity for item in self.items):
            self.items.append(entity)

    def find(self, criteria):
        return [item for item in self.items if criteria(item)]


class Repository(StorageDB):
    def __init__(self, storage: StorageDB):
        self.storage = storage

    def save(self, entity):
        self.storage.save(entity)

    def find(self, criteria):
        return self.storage.find(criteria)


class ReviewRepository(Repository):
    def save_review(self, review):
        self.save(review)

    def get_reviews(self, predicate=lambda review: True):
        return self.find(lambda item: isinstance(item, Review) and predicate(item))

    def save_reply(self, reply):
        if self.find(lambda item: isinstance(item, ManagerReply) and item.review_id == reply.review_id):
            raise ValueError("У отзыва уже есть ответ")
        self.save(reply)

    def get_reply(self, review_id):
        return next(iter(self.find(lambda item: isinstance(item, ManagerReply) and item.review_id == review_id)), None)

    def save_draft(self, draft):
        self.save(draft)


class UserRepository(Repository):
    def save_profile(self, profile):
        self.save(profile)

    def get_profile(self, profile_id):
        return next(iter(self.find(lambda item: isinstance(item, UserProfile) and item.id == profile_id)), None)


class AnalyticsRepository(Repository):
    def __init__(self, storage):
        super().__init__(storage)
        self.results = {}

    def save_result(self, result, review_id):
        self.results[review_id] = result
        self.save(result)

    def get_result(self, review_id):
        return self.results.get(review_id)


class TaskQueue:
    def __init__(self):
        self.tasks = deque()

    def add_task(self, review):
        self.tasks.append(review)

    def take_task(self):
        return self.tasks.popleft() if self.tasks else None


class EventHandler(ABC):
    @abstractmethod
    def handle(self, review): ...


class ObservableTaskQueue(TaskQueue):
    def __init__(self):
        super().__init__()
        self.subscribers = []

    def subscribe(self, handler: EventHandler):
        self.subscribers.append(handler)

    def notify_subscribers(self, review):
        for handler in self.subscribers:
            handler.handle(review)


class FakeDetectionModule(EventHandler):
    def __init__(self):
        self.histories, self.text_counts = {}, Counter()

    def handle(self, review):
        history = self.histories.setdefault(review.client_id, ActivityHistory())
        activity = self.analyze_activity(history)
        risk = self.calculate_risk(activity, self.check_style(review.text))
        review.suspicious, review.trust_level = risk >= 0.6, round(1 - risk, 2)

    def analyze_activity(self, history):
        history.activity_times.append(datetime.now())
        history.review_frequency = sum((datetime.now() - time).total_seconds() < 60 for time in history.activity_times)
        return min(0.5, max(0, history.review_frequency - 3) * 0.15)

    def check_style(self, text):
        normalized = " ".join(tokens(text))
        self.text_counts[normalized] += 1
        return min(0.8, (0.35 if len(tokens(text)) < 3 else 0) + (0.6 if self.text_counts[normalized] > 1 else 0))

    def calculate_risk(self, activity, style):
        return min(1.0, activity + style)


class AnalysisModule:
    def tokenize(self, text):
        return tokens(text)

    def normalize(self, text):
        return " ".join(text.casefold().replace("ё", "е").split())

    def determine_sentiment(self, text):
        score = sentiment_score(self.tokenize(text))
        return "Позитивная" if score > 0 else "Негативная" if score < 0 else "Нейтральная"

    def extract_entities(self, text):
        return [entity for entity in ENTITIES if entity in text]

    def classify(self, text):
        return [name for name, stems in CATEGORIES.items() if any(stem in text for stem in stems)] or ["Общее"]

    def analyze(self, review):
        text = self.normalize(review.text)
        return AnalysisResult(self.determine_sentiment(text), self.classify(text), self.extract_entities(text))


class MetricsModule:
    def calculate_nps(self, reviews):
        return nps(reviews)

    def calculate_dynamics(self, reviews):
        return dict(sorted(Counter(r.created_at.isoformat() for r in reviews).items()))


class ExtendedMetricsModule(MetricsModule):
    def calculate_correlation(self, reviews):
        return pearson([(r.rating, r.recommendation) for r in reviews if r.recommendation is not None])


class AnalyticalModule:
    def __init__(self, repository, metrics):
        self.repository, self.metrics = repository, metrics

    def find_correlations(self, reviews=None):
        value = self.metrics.calculate_correlation(self.source(reviews))
        return [("Оценка и готовность рекомендовать", value)]

    def source(self, reviews):
        return self.repository.get_reviews() if reviews is None else reviews

    def identify_trends(self, reviews=None):
        ordered = sorted(self.source(reviews), key=lambda review: review.created_at)
        return self.rating_trend(ordered)

    def rating_trend(self, ordered):
        if len(ordered) < 2:
            return []
        middle = len(ordered) // 2
        delta = self.average(ordered[middle:]) - self.average(ordered[:middle])
        return [Trend("Средняя оценка", "Первая и вторая половина периода", "Рост" if delta > 0.1 else "Снижение" if delta < -0.1 else "Стабильно")]

    def average(self, reviews):
        return sum(r.rating for r in reviews) / len(reviews)

    def segment_clients(self, reviews=None):
        groups = self.client_groups(self.source(reviews))
        return [CustomerSegment(name, f"{len(clients)} клиентов") for name, clients in groups.items()]

    def client_groups(self, reviews):
        ids = {r.client_id for r in reviews}
        means = {key: self.average([r for r in reviews if r.client_id == key]) for key in ids}
        return {name: [key for key, mean in means.items() if predicate(mean)] for name, predicate in
                {"Довольные": lambda x: x >= 4, "Нейтральные": lambda x: 3 <= x < 4, "Недовольные": lambda x: x < 3}.items()}


class ReportModule:
    def __init__(self, storage, metrics):
        self.storage, self.metrics = storage, metrics

    def form_report(self, period, reviews):
        report = Report(period=period, metrics=summary(reviews))
        self.storage.save(report)
        return report


class Notification:
    def __init__(self):
        self.messages = []

    def send(self, recipient, text):
        self.messages.append((recipient, text))


class TextGenerator:
    def generate_reply(self, review_text, sentiment):
        category = AnalysisModule().classify(review_text)[0]
        opening = "Спасибо за высокую оценку!" if sentiment == "Позитивная" else "Спасибо, что сообщили о проблеме." if sentiment == "Негативная" else "Спасибо за обратную связь."
        return f"{opening} Ваш отзыв по теме «{category.lower()}» принят. " + ("Передадим детали ответственному специалисту для проверки." if sentiment == "Негативная" else "Мы учтём ваш опыт при улучшении сервиса.")


class InputInterface(ABC):
    @abstractmethod
    def submit(self, review): ...


class WebForm(InputInterface):
    def __init__(self, reviews, queue):
        self.reviews, self.queue = reviews, queue

    def fill_form(self, review):
        return review

    def submit(self, review):
        self.reviews.save_review(review)
        self.queue.add_task(review)


class ManagerPanel:
    def __init__(self, reviews):
        self.reviews = reviews

    def open_review_list(self, predicate=lambda review: True):
        return self.reviews.get_reviews(predicate)

    def write_reply(self, manager, review, text):
        return manager.write_reply(review, text)

    def send_reply(self, reply):
        self.reviews.save_reply(reply)


class ExtendedManagerPanel(ManagerPanel):
    def __init__(self, reviews, generator):
        super().__init__(reviews)
        self.generator = generator

    def request_draft(self, review, result):
        return ReviewDraft(review_id=review.id, text=self.generator.generate_reply(review.text, result.sentiment), status="Сгенерирован")

    def edit_draft(self, draft, text):
        draft.text = text
        self.reviews.save_draft(draft)

    def show_suspicious_label(self, review):
        return review.suspicious


class Dashboard:
    def __init__(self, metrics):
        self.metrics = metrics

    def show_charts(self, reviews):
        return Chart(chart_type="Динамика"), self.metrics.calculate_dynamics(reviews)


class ExtendedDashboard(Dashboard):
    def __init__(self, metrics, analytics):
        super().__init__(metrics)
        self.analytics = analytics

    def trends(self, reviews=None):
        return self.analytics.identify_trends(reviews)

    def correlations(self, reviews=None):
        return self.analytics.find_correlations(reviews)


class SurveyService:
    """Local invitations; no external email delivery is implied."""
    def __init__(self, notifications):
        self.notifications, self.invitations = notifications, []

    def launch(self, product, clients):
        recipients = list(dict.fromkeys(clients))
        for client in recipients:
            self.notifications.send(client, f"Приглашение: оставьте отзыв о {product.name}")
        self.invitations.append((product.id, recipients))
        return len(recipients)
