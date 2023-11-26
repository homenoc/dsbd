from django.db import models
from django.db.models import Q
from django.utils import timezone

from dsbd.models import MediumTextField


class NoticeManager(models.Manager):
    def get_notice(self):
        now = timezone.now()
        notices = self.filter(
            Q(start_at__lte=now),
            Q(is_active=True),
            Q(end_at__gt=timezone.now()) | Q(end_at__isnull=True)
        )
        return notices


class Notice(models.Model):
    class Meta:
        ordering = ("-end_at",)

    SERVICE = "サービス情報"
    ETC = "その他"

    TYPE1_CHOICES = (
        (SERVICE, SERVICE),
        (ETC, ETC),
    )

    created_at = models.DateTimeField("作成日", default=timezone.now, db_index=True)
    start_at = models.DateTimeField("通知開始日", default=timezone.now)
    end_at = models.DateTimeField("通知終了日", blank=True, null=True)
    is_active = models.BooleanField("有効", default=True)
    type1 = models.CharField("type1", max_length=200, choices=TYPE1_CHOICES)
    title = models.CharField("title", max_length=250)
    body = MediumTextField(verbose_name="内容", default="", blank=True)
    is_important = models.BooleanField("重要", default=False)
    is_fail = models.BooleanField("障害", default=False)
    is_info = models.BooleanField("情報", default=False)

    objects = NoticeManager()

    def __str__(self):
        return "%s: %s" % (self.id, self.title)
