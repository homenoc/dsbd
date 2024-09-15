from django.apps import AppConfig


class Notice(AppConfig):
    name = "notice"
    verbose_name = "通知"

    def ready(self):
        from . import signals  # noqa
