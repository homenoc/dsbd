from django.db import models
from django.utils import timezone

from dsbd.models import MediumTextField
from noc.models import NOC


class TunnelRouter(models.Model):
    class Meta:
        ordering = ("id",)
        verbose_name = "Tunnel Router"
        verbose_name_plural = "Tunnel Routers"

    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    is_active = models.BooleanField("有効", default=True)
    noc = models.ForeignKey(NOC, on_delete=models.CASCADE)
    hostname = models.CharField("ホスト名", unique=True, max_length=255)
    comment = MediumTextField("コメント", default="", blank=True)


class TunnelIP(models.Model):
    class Meta:
        ordering = ("id",)
        verbose_name = "Tunnel IP"
        verbose_name_plural = "Tunnel IPs"

    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    is_active = models.BooleanField("有効", default=True)
    tunnel_router = models.ForeignKey(TunnelRouter, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField("IPアドレス", unique=True)
    comment = MediumTextField("コメント", default="", blank=True)
