"""Composition root: main/injector responsibilities only."""
from types import SimpleNamespace
from .models import Company, Product
from .accounts import AccountService
from .services import (
    InMemoryStorage, ObservableTaskQueue, ReviewRepository, UserRepository,
    AnalyticsRepository, Notification, ExtendedMetricsModule, AnalyticalModule,
    AnalysisModule, FakeDetectionModule, ReportModule, ExtendedManagerPanel,
    TextGenerator, ExtendedDashboard, WebForm, SurveyService,
)
from .controllers import AnalysisController, ReviewController, ReplyController


def create_services():
    services = SimpleNamespace(storage=InMemoryStorage(), queue=ObservableTaskQueue())
    create_repositories(services)
    create_modules(services)
    create_boundaries(services)
    return services


def create_repositories(s):
    s.reviews = ReviewRepository(s.storage)
    s.users = UserRepository(s.storage)
    s.results = AnalyticsRepository(s.storage)
    s.notifications = Notification()
    s.auth = AccountService(s.users)


def create_modules(s):
    s.metrics = ExtendedMetricsModule()
    s.analytics = AnalyticalModule(s.reviews, s.metrics)
    s.analysis = AnalysisController(AnalysisModule(), s.results)
    s.queue.subscribe(FakeDetectionModule())


def create_boundaries(s):
    create_reporting(s)
    s.panel = ExtendedManagerPanel(s.reviews, TextGenerator())
    s.dashboard = ExtendedDashboard(s.metrics, s.analytics)
    s.submit = ReviewController(WebForm(s.reviews, s.queue), s.queue, s.analysis, s.notifications)
    s.reply = ReplyController(s.panel, s.notifications)


def create_catalog(storage):
    company = Company(name="Демонстрационная компания")
    product = Product(name="Демонстрационный продукт", company_id=company.id)
    storage.save(company)
    storage.save(product)
    return company, product


def create_reporting(s):
    s.reports = ReportModule(s.storage, s.metrics)
    s.surveys = SurveyService(s.notifications)
