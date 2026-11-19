"""Классы данных и пользователи из диаграмм классов, стр. 12–15."""
from abc import ABC
from dataclasses import dataclass, field
from datetime import date

@dataclass
class User(ABC):
    id: str = ""
    email: str = ""

@dataclass
class Client(User):
    def leave_review(self):
        return None

    def view_history(self):
        return None

@dataclass
class Manager(User):
    def read_review(self):
        return None

    def reply_to_review(self):
        return None

@dataclass
class BusinessAnalyst(User):
    def request_analytics(self):
        return None

@dataclass
class Review:
    id: str = ""
    text: str = ""
    rating: int = 0
    anonymous: bool = False
    date: date = field(default_factory=date.today)
    suspicious: bool = False
    trust_level: float = 0.0

@dataclass
class ManagerReply:
    text: str = ""
    date: date = field(default_factory=date.today)
    generated_automatically: bool = False

@dataclass
class AnalysisResult:
    sentiment: str = ""
    categories: list[str] = field(default_factory=list)
    key_entities: list[str] = field(default_factory=list)

@dataclass
class Product:
    id: str = ""
    name: str = ""

@dataclass
class Company:
    id: str = ""
    name: str = ""

@dataclass
class UserProfile:
    id: str = ""

@dataclass
class Report:
    id: str = ""
    period: str = ""
    metrics: dict = field(default_factory=dict)

@dataclass
class ReplyDraft:
    text: str = ""
    status: str = ""

@dataclass
class Trend:
    metric: str = ""
    period: str = ""
    direction: str = ""

@dataclass
class CustomerSegment:
    name: str = ""
    criteria: str = ""

@dataclass
class ActivityHistory:
    network_address: str = ""
    devices: list[str] = field(default_factory=list)
    publication_frequency: int = 0
    activity_times: list[date] = field(default_factory=list)
