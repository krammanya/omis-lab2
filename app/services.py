"""In-memory services and repositories used by the interface prototype."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter

from .models import (
    AnalysisResult, CustomerSegment, Manager, ManagerReply, Report, Review,
    ReviewDraft, Trend, UserProfile,
)


class StorageDB(ABC):
    @abstractmethod
    def save(self, entity: object) -> None: ...

    @abstractmethod
    def find_all(self, entity_type: type) -> list: ...


class InMemoryStorage(StorageDB):
    """Simple storage adapter; replaceable by a database implementation."""

    def __init__(self) -> None:
        self._items: dict[type, list] = {}

    def save(self, entity: object) -> None:
        bucket = self._items.setdefault(type(entity), [])
        if entity not in bucket:
            bucket.append(entity)

    def find_all(self, entity_type: type) -> list:
        return list(self._items.get(entity_type, []))


class ReviewRepository:
    def __init__(self, storage: StorageDB) -> None:
        self.storage = storage

    def save_review(self, review: Review) -> None:
        self.storage.save(review)

    def get_reviews(self) -> list[Review]:
        return self.storage.find_all(Review)

    def save_reply(self, reply: ManagerReply) -> None:
        self.storage.save(reply)

    def save_draft(self, draft: ReviewDraft) -> None:
        self.storage.save(draft)


class UserRepository:
    def __init__(self, storage: StorageDB) -> None:
        self.storage = storage

    def save_profile(self, profile: object) -> None:
        self.storage.save(profile)

    def get_profile(self, profile_id: str) -> object | None:
        return next((profile for profile in self.storage.find_all(UserProfile) if profile.id == profile_id), None)


class AnalyticsRepository:
    def __init__(self, storage: StorageDB) -> None:
        self.storage = storage

    def save_result(self, result: AnalysisResult) -> None:
        self.storage.save(result)


class TaskQueue:
    def __init__(self) -> None:
        self.tasks: list[str] = []
        self.subscribers: list[EventHandler] = []

    def add_task(self, task: str) -> None:
        self.tasks.append(task)

    def take_task(self) -> str | None:
        return self.tasks.pop(0) if self.tasks else None

    def subscribe(self, handler: EventHandler) -> None:
        self.subscribers.append(handler)

    def notify_subscribers(self, review: Review) -> None:
        for handler in self.subscribers:
            handler.handle(review)


class EventHandler(ABC):
    @abstractmethod
    def handle(self, review: Review) -> None: ...


class FakeDetectionModule(EventHandler):
    def handle(self, review: Review) -> None:
        self.analyze_activity()
        self.check_style()
        self.calculate_risk()

    def analyze_activity(self) -> None:
        pass

    def check_style(self) -> None:
        pass

    def calculate_risk(self) -> None:
        pass


class AnalysisModule:
    """Small demonstration of the analysis classes in the class diagrams."""

    CATEGORIES = ("Качество", "Доставка", "Обслуживание")

    def tokenize(self, text: str) -> list[str]:
        return text.split()

    def normalize(self, text: str) -> str:
        return text.casefold()

    def determine_sentiment(self, review: Review) -> str:
        return self.analyze(review).sentiment

    def extract_entities(self, review: Review) -> list[str]:
        return self.analyze(review).key_entities

    def classify(self, review: Review) -> list[str]:
        return self.analyze(review).categories

    def analyze(self, review: Review) -> AnalysisResult:
        text = review.text.casefold()
        negative = any(word in text for word in ("плохо", "долго", "сломал", "ужас"))
        positive = any(word in text for word in ("хорошо", "быстро", "отлично", "спасибо"))
        sentiment = "Негативная" if negative else "Позитивная" if positive else "Нейтральная"
        categories = [category for category, words in {
            "Качество": ("качеств", "сломал", "товар"),
            "Доставка": ("достав", "долго", "курьер"),
            "Обслуживание": ("поддержк", "менеджер", "сервис"),
        }.items() if any(word in text for word in words)]
        result = AnalysisResult(sentiment, categories, [], review.suspicious, 0.0)
        return result

    def detect_manipulation(self, reviews: list[Review]) -> list[Review]:
        for review in reviews:
            review.suspicious = len(review.text.strip()) < 8
        return reviews


class MetricsModule:
    def calculate_nps(self, reviews: list[Review]) -> int:
        if not reviews:
            return 0
        return round(sum(review.rating for review in reviews) / len(reviews) * 20 - 100)

    def calculate_dynamics(self, reviews: list[Review]) -> dict[str, int]:
        return dict(Counter(review.created_at.strftime("%m.%Y") for review in reviews))

    def calculate_correlation(self) -> float:
        return 0.0


class ReportModule:
    def form_report(self, period: str, reviews: list[Review]) -> Report:
        return Report(period=period)


class Notification:
    def send(self, manager: Manager, review: Review) -> str:
        return f"Уведомление для {manager.name}: получен новый отзыв {review.id[:8]}"


class TextGenerator:
    def generate_reply(self, review: Review, sentiment: str) -> str:
        if sentiment == "Негативная":
            return "Спасибо за обратную связь. Нам жаль, что возникла такая ситуация. Мы разберёмся и свяжемся с вами."
        return "Спасибо за ваш отзыв! Мы ценим обратную связь."


class AnalyticalModule:
    def find_correlations(self) -> list[tuple[str, str]]:
        return []

    def identify_trends(self) -> list[Trend]:
        return []

    def segment_clients(self) -> list[CustomerSegment]:
        return []


class Dashboard:
    def __init__(self, metrics: MetricsModule) -> None:
        self.metrics = metrics

    def show_charts(self, reviews: list[Review]) -> dict[str, int]:
        return self.metrics.calculate_dynamics(reviews)


class InputInterface(ABC):
    @abstractmethod
    def submit(self, review: Review, repository: ReviewRepository) -> None: ...


class WebForm(InputInterface):
    """Boundary object for review input; desktop prototype supplies the form UI."""

    def submit(self, review: Review, repository: ReviewRepository) -> None:
        repository.save_review(review)

    def fill_form(self, review: Review) -> Review:
        return review


class ManagerPanel:
    """Operations of the manager boundary shown on the class diagrams."""

    def __init__(self, repository: ReviewRepository, generator: TextGenerator) -> None:
        self.repository = repository
        self.generator = generator

    def open_review_list(self) -> list[Review]:
        return self.repository.get_reviews()

    def write_reply(self, manager: Manager, review: Review, text: str) -> ManagerReply:
        return manager.write_reply(review, text)

    def send_reply(self, reply: ManagerReply) -> None:
        self.repository.save_reply(reply)

    def request_draft(self, review: Review, sentiment: str) -> ReviewDraft:
        return ReviewDraft(review_id=review.id, text=self.generator.generate_reply(review, sentiment))

    def edit_draft(self, draft: ReviewDraft, text: str) -> None:
        draft.text = text

    def show_suspicious_label(self, review: Review) -> bool:
        return review.suspicious
