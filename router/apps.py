from django.apps import AppConfig


class CustomAdmin(AppConfig):
    name = "router"
    verbose_name = "Router"

    def ready(self):
        from . import signals  # noqa
