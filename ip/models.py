from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from custom_auth.models import Group
from dsbd.models import MediumTextField
from service.models import Service

OWNER_TYPE_FROM_OUR = "form_our"
OWNER_TYPE_FROM_YOUR = "form_your"
OWNER_TYPE_CHOICES = (
    (OWNER_TYPE_FROM_OUR, "当団体から割当"),
    (OWNER_TYPE_FROM_YOUR, "貴団体から割当"),
)

IP_VERSION_4 = 4
IP_VERSION_6 = 6
IP_VERSION_CHOICES = (
    (IP_VERSION_4, "IPv4"),
    (IP_VERSION_6, "IPv6"),
)


class IP(models.Model):
    class Meta:
        ordering = ("id",)
        verbose_name = "IP"
        verbose_name_plural = "IPs"

    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    is_active = models.BooleanField("有効", default=True)
    is_pass = models.BooleanField("審査OK", default=False)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, related_name="IPService", null=True, blank=True)
    version = models.IntegerField("IPバージョン", choices=IP_VERSION_CHOICES, default=IP_VERSION_4)
    ip_address = models.GenericIPAddressField("IP Address", null=True, blank=True)
    subnet = models.IntegerField("サブネット", default=32)
    owner = models.CharField(
        "アドレス所持オーナ", default=OWNER_TYPE_FROM_OUR, choices=OWNER_TYPE_CHOICES, max_length=255
    )
    start_at = models.DateTimeField("開通日", null=True, blank=True)
    end_at = models.DateTimeField("解約日", null=True, blank=True)
    ipv4_plan = models.JSONField("IPv4プラン", null=True, blank=True)
    use_case = MediumTextField("使用用途", default="", blank=True)
    jpnic_user = models.ManyToManyField(
        "JPNICUser",
        blank=True,
        through="IPJPNICUser",
        through_fields=("ip", "jpnic_user"),
        related_name="jpnic_user_set",
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%d: %s/%s" % (self.id, self.ip_address, self.subnet)


HANDLE_TYPE_GROUP = "group_handle"
HANDLE_TYPE_JPNIC = "jpnic_handle"

HANDLE_TYPE_CHOICES = (
    (HANDLE_TYPE_GROUP, "グループハンドル"),
    (HANDLE_TYPE_JPNIC, "JPNICハンドル"),
)


class JPNICUser(models.Model):
    class Meta:
        ordering = ("id",)
        verbose_name = "JPNIC User"
        verbose_name_plural = "JPNIC Users"
        unique_together = ("group", "jpnic_handle", "version", "name", "name_jp")

    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    group = models.ForeignKey(Group, related_name="JPNICUserGroup", on_delete=models.CASCADE)
    is_pass = models.BooleanField("審査OK", default=False)
    hidden = models.BooleanField("隠蔽", default=False)
    handle_type = models.CharField(
        "ハンドルタイプ", max_length=255, choices=HANDLE_TYPE_CHOICES, default=HANDLE_TYPE_JPNIC
    )
    version = models.IntegerField("IPバージョン", choices=IP_VERSION_CHOICES, default=IP_VERSION_4)
    jpnic_handle = models.CharField("JPNIC Handle", max_length=100, blank=True)
    name = models.CharField("name", max_length=150)
    name_jp = models.CharField("name(japanese)", max_length=150)
    email = models.EmailField("E-Mail", max_length=150)
    org = models.CharField("Org", max_length=150)
    org_jp = models.CharField("Org(japanese)", max_length=150)
    postcode = models.CharField("郵便番号", max_length=20, default="")
    address = models.CharField("住所", max_length=250, default="")
    address_jp = models.CharField("住所(Japanese)", max_length=250, default="")
    dept = models.CharField("部署", max_length=250, default="", blank=True)
    dept_jp = models.CharField("部署(Japanese)", max_length=250, default="", blank=True)
    title = models.CharField("役職", max_length=250, default="", blank=True)
    title_jp = models.CharField("役職(Japanese)", max_length=250, default="", blank=True)
    tel = models.CharField("tel", max_length=30, default="")
    fax = models.CharField("fax", max_length=30, default="", blank=True)
    country = models.CharField("居住国", max_length=100, default="Japan")
    ip = models.ManyToManyField(
        "IP",
        blank=True,
        through="IPJPNICUser",
        through_fields=("jpnic_user", "ip"),
        related_name="jpnic_set",
    )
    history = HistoricalRecords()

    def __str__(self):
        return "%d: %s(%s)" % (self.id, self.name, self.name_jp)


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
    user_type = models.CharField(
        "タイプ", max_length=255, choices=JPNIC_USER_TYPE_CHOICES, default=JPNIC_USER_TYPE_ADMIN
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "IP・JPNIC User"
        verbose_name_plural = "IP・JPNIC Users"
        unique_together = ("jpnic_user", "ip", "user_type")

    def __str__(self):
        return "%s" % (self.id,)
