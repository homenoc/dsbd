from django.apps import AppConfig


class Ticket(AppConfig):
    name = "ticket"
    verbose_name = "チケット"

    def ready(self):
        pass
