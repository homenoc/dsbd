from django.db import models
from django.utils import timezone

from dsbd.models import MediumTextField


class NOC(models.Model):
    class Meta:
        ordering = ("id",)
        verbose_name = "NOC"
        verbose_name_plural = "NOCs"

    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    name = models.CharField("名前", default="", max_length=255)
    is_active = models.BooleanField("有効", default=True)
    location = models.CharField("場所", default="", max_length=255, blank=True)
    bandwidth = models.IntegerField("帯域幅", default=1000)
    comment = MediumTextField("コメント", default="", blank=True)
