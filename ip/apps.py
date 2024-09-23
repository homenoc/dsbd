from django.apps import AppConfig


class CustomAdmin(AppConfig):
    name = "ip"
    verbose_name = "IP"

    def ready(self):
        from . import signals  # noqa
