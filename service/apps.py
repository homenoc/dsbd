from django.apps import AppConfig


class CustomAdmin(AppConfig):
    name = "service"
    verbose_name = "Service"

    def ready(self):
        from . import signals  # noqa
