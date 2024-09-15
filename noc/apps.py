from django.apps import AppConfig


class CustomAdmin(AppConfig):
    name = "noc"
    verbose_name = "NOC"

    def ready(self):
        from . import signals  # noqa
