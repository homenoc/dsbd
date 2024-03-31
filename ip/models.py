from django.db import models
from django.utils import timezone

from custom_auth.models import Group
from dsbd.models import MediumTextField
from service.models import Service

SERVICE_L2 = "2000"
SERVICE_L3_STATIC = "3S00"
SERVICE_L3_BGP = "3B00"
SERVICE_TRANSIT = "IP3B"
SERVICE_COLO_L2 = "CL20"
SERVICE_COLO_L3_STATIC = "CL3S"
SERVICE_COLO_L3_BGP = "CL3B"
SERVICE_ETC = "ET00"

SERVICE_CHOICES = (
    (SERVICE_L2, "L2"),
    (SERVICE_L3_STATIC, "L3 Static"),
    (SERVICE_L3_BGP, "L3 BGP"),
    (SERVICE_TRANSIT, "トランジット提供"),
    (SERVICE_COLO_L2, "コロケーションサービス(L2)"),
    (SERVICE_COLO_L3_STATIC, "コロケーションサービス(L3 Static)"),
    (SERVICE_COLO_L3_BGP, "コロケーションサービス(L3 BGP)"),
    (SERVICE_ETC, "その他"),
)


class IP(models.Model):
    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    is_active = models.BooleanField("有効", default=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, related_name="IPService", null=True, blank=True)
    ip_address = models.GenericIPAddressField("IP Address", unique=True)
    subnet = models.IntegerField("サブネット", default=32)
    start_at = models.DateTimeField("開通日", null=True, blank=True)
    end_at = models.DateTimeField("解約日", null=True, blank=True)
    plan = models.JSONField("プラン", null=True, blank=True)
    use_case = MediumTextField("使用用途", default="")
    jpnic_user = models.ManyToManyField(
        "JPNICUser",
        blank=True,
        through='IPJPNICUser',
        through_fields=('ip', 'jpnic_user'),
        related_name="jpnic_user_set",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "IP"
        verbose_name_plural = "IPs"


HANDLE_TYPE_GROUP = "group_handle"
HANDLE_TYPE_JPNIC = "jpnic_handle"

HANDLE_TYPE_CHOICES = (
    (HANDLE_TYPE_GROUP, "グループハンドル"),
    (HANDLE_TYPE_JPNIC, "JPNICハンドル"),
)


class JPNICUser(models.Model):
    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_active = models.BooleanField("有効", default=True)
    hidden = models.BooleanField("隠蔽", default=False)
    handle_type = models.CharField("ハンドルタイプ", max_length=255, choices=HANDLE_TYPE_CHOICES, default=HANDLE_TYPE_JPNIC)
    jpnic_handle = models.CharField("JPNIC Handle", max_length=100, blank=True)
    name = models.CharField("name", max_length=150)
    name_jp = models.CharField("name(japanese)", max_length=150)
    email = models.EmailField("E-Mail", max_length=150)
    org = models.CharField("Org", max_length=150, unique=True)
    org_jp = models.CharField("Org(japanese)", max_length=150)
    postcode = models.CharField("郵便番号", max_length=20, default="")
    address = models.CharField("住所", max_length=250, default="")
    address_jp = models.CharField("住所(Japanese)", max_length=250, default="")
    dept = models.CharField("部署", max_length=250, default="", blank=True)
    dept_jp = models.CharField("部署(Japanese)", max_length=250, default="", blank=True)
    title = models.CharField("役職", max_length=250, default="", blank=True)
    title_jp = models.CharField("役職(Japanese)", max_length=250, default="", blank=True)
    tel = models.CharField("tel", max_length=30, default="")
    fax = models.CharField("fax", max_length=30, default="")
    country = models.CharField("居住国", max_length=100, default="Japan")
    ip = models.ManyToManyField(
        "IP",
        blank=True,
        through='IPJPNICUser',
        through_fields=('jpnic_user', 'ip'),
        related_name="jpnic_set",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "JPNIC User"
        verbose_name_plural = "JPNIC Users"


JPNIC_USER_TYPE_ADMIN = "admin"
JPNIC_USER_TYPE_TECH_1 = "tech1"
JPNIC_USER_TYPE_TECH_2 = "tech2"
JPNIC_USER_TYPE_TECH_3 = "tech3"
JPNIC_USER_TYPE_TECH_4 = "tech4"
JPNIC_USER_TYPE_TECH_5 = "tech5"

JPNIC_USER_TYPE_CHOICES = (
    (JPNIC_USER_TYPE_ADMIN, "管理者"),
    (JPNIC_USER_TYPE_TECH_1, "技術担当者1"),
    (JPNIC_USER_TYPE_TECH_2, "技術担当者2"),
    (JPNIC_USER_TYPE_TECH_3, "技術担当者3"),
    (JPNIC_USER_TYPE_TECH_4, "技術担当者4"),
    (JPNIC_USER_TYPE_TECH_5, "技術担当者5"),
)


class IPJPNICUser(models.Model):
    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    jpnic_user = models.ForeignKey(JPNICUser, on_delete=models.CASCADE)
    ip = models.ForeignKey(IP, on_delete=models.CASCADE)
    user_type = models.CharField("タイプ", max_length=255, choices=JPNIC_USER_TYPE_CHOICES, default=JPNIC_USER_TYPE_ADMIN)

    class Meta:
        verbose_name = 'IP・JPNIC User'
        verbose_name_plural = "IP・JPNIC Users"
        unique_together = ('jpnic_user', 'ip')

    def __str__(self):
        return "%s" % (self.id,)
