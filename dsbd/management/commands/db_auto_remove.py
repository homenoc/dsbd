from django.core.management.base import BaseCommand
from django.utils import timezone

from notice.models import Notice


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("batch process for db_auto_remove")
        now = timezone.now()
        # 掲載終了の通知情報を削除
        Notice.objects.filter(end_at__lt=now).delete()
