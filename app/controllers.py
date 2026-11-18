"""Sequence participants and minimal coordination of UML collaborators."""
from .models import Review, AnalysisResult


class AnalysisController:
    def __init__(self, module, repository):
        self.module, self.repository = module, repository

    def process(self, review):
        self.repository.save_result(self.module.analyze(review), review.id)


class ReviewController:
    def __init__(self, form, queue, analysis, notifications):
        self.form, self.queue = form, queue
        self.analysis, self.notifications = analysis, notifications

    def submit(self, review):
        self.form.submit(self.form.fill_form(review))
        self.process_next()

    def process_next(self):
        review = self.queue.take_task()
        self.analysis.process(review)
        self.queue.notify_subscribers(review)
        self.notifications.send("manager", "Получен новый отзыв")


class ReplyController:
    def __init__(self, panel, notifications):
        self.panel, self.notifications = panel, notifications

    def send(self, manager, review, text, generated=False):
        reply = self.panel.write_reply(manager, review, text)
        reply.generated_automatically = generated
        self.panel.send_reply(reply)
        review.reply_id = reply.id
        self.notifications.send(review.client_id, "Получен ответ")
