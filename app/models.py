"""Классы пользователей и данных с базовой диаграммы классов."""
from abc import ABC
from datetime import date

class User(ABC):
    id: str = ""
    email: str = ""

class Client(User):
    def leave_review(self):
        return None

    def view_history(self):
        return None

class Manager(User):
    def read_review(self):
        return None

    def reply_to_review(self):
        return None

class BusinessAnalyst(User):
    def request_analytics(self):
        return None

class Review:
    id: str = ""
    text: str = ""
    rating: int = 0
    anonymous: bool = False
    date: date

class ManagerReply:
    text: str = ""
    date: date

class AnalysisResult:
    sentiment: str = ""
    categories: list[str]
    key_entities: list[str]

class Product:
    id: str = ""
    name: str = ""

class Company:
    id: str = ""
    name: str = ""

class UserProfile:
    id: str = ""

class Report:
    id: str = ""
    period: str = ""
    metrics: dict

