"""Domain objects corresponding to the supplied UML class diagrams."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


def new_id() -> str:
    return str(uuid4())


class Role(str, Enum):
    CLIENT = "Клиент"
    MANAGER = "Менеджер"
    ANALYST = "Бизнес-аналитик"


@dataclass
class User:
    id: str = field(default_factory=new_id)
    email: str = ""


@dataclass
class Client(User):
    name: str = "Клиент"
    authorization_type: str = "личный кабинет"
    profile: Optional["UserProfile"] = None

    def leave_review(self, review: "Review") -> None:
        review.client_id = self.id

    def view_history(self, reviews: list["Review"]) -> list["Review"]:
        return [review for review in reviews if review.client_id == self.id]


@dataclass
class Manager(User):
    name: str = "Менеджер"
    work_experience: str = ""

    def read_review(self, review: "Review") -> str:
        return review.text

    def write_reply(self, review: "Review", text: str) -> "ManagerReply":
        return ManagerReply(text=text, review_id=review.id, manager_id=self.id)


@dataclass
class BusinessAnalyst(User):
    name: str = "Бизнес-аналитик"
    work_experience: str = ""

    def request_analytics(self, metrics: list["Metric"]) -> list["Metric"]:
        return metrics


@dataclass
class Review:
    id: str = field(default_factory=new_id)
    text: str = ""
    rating: int = 0
    anonymous: bool = False
    created_at: date = field(default_factory=date.today)
    client_id: str = ""
    product_id: str = ""
    company_id: str = ""
    suspicious: bool = False
    trust_level: float = 0.0
    reply_id: Optional[str] = None


@dataclass
class ManagerReply:
    id: str = field(default_factory=new_id)
    text: str = ""
    created_at: date = field(default_factory=date.today)
    review_id: str = ""
    manager_id: str = ""
    generated_automatically: bool = False


@dataclass
class AnalysisResult:
    sentiment: str = "Нейтральная"
    categories: list[str] = field(default_factory=list)
    key_entities: list[str] = field(default_factory=list)
    suspicious: bool = False
    manipulation_level: float = 0.0


@dataclass
class Product:
    id: str = field(default_factory=new_id)
    name: str = ""
    company_id: str = ""


@dataclass
class Company:
    id: str = field(default_factory=new_id)
    name: str = ""


@dataclass
class UserProfile:
    id: str = field(default_factory=new_id)
    client_id: str = ""


@dataclass
class Metric:
    id: str = field(default_factory=new_id)
    name: str = ""
    value: float = 0.0
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Report:
    id: str = field(default_factory=new_id)
    period: str = "Месяц"
    metrics: dict = field(default_factory=dict)


@dataclass
class Chart:
    id: str = field(default_factory=new_id)
    chart_type: str = "Динамика"


@dataclass
class ReviewDraft:
    """Optional manager reply draft shown in the draft extension diagram."""

    review_id: str = ""
    text: str = ""
    status: str = "Черновик"


@dataclass
class Reply:
    id: str = field(default_factory=new_id)
    text: str = ""
    review_id: str = ""


@dataclass
class ReviewAnalytics:
    sentiment: str = "Нейтральная"
    categories: list[str] = field(default_factory=list)
    key_entities: list[str] = field(default_factory=list)


@dataclass
class Trend:
    metric: str = ""
    period: str = "Месяц"
    direction: str = "Стабильно"


@dataclass
class CustomerSegment:
    name: str = ""
    criteria: str = ""


@dataclass
class ActivityHistory:
    network_address: str = ""
    devices: list[str] = field(default_factory=list)
    review_frequency: int = 0
    activity_times: list[datetime] = field(default_factory=list)
