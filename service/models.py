from django.db import models
from django.db.models import Q
from django.utils import timezone

from custom_auth.models import Group
from dsbd.models import MediumTextField
from router.models import TunnelIP


class ServiceManager(models.Manager):
    def get_notice(self):
        now = timezone.now()
        notices = self.filter(
            Q(start_at__lte=now),
            Q(is_active=True),
            Q(end_at__gt=timezone.now()) | Q(end_at__isnull=True)
        )
        return notices


class Service(models.Model):
    class Meta:
        ordering = ("id",)
        verbose_name = "Service"
        verbose_name_plural = "Services"

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

    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name="ServiceGroup", null=True, blank=True)
    service_type = models.IntegerField("サービスタイプ", choices=SERVICE_CHOICES, default=SERVICE_COLO_L3_BGP)
    service_number = models.IntegerField("サービス番号", default=0)
    service_comment = models.IntegerField("サービス情報コメント", default=0, blank=True)
    is_active = models.BooleanField("有効", default=True)
    is_pass = models.BooleanField("審査OK", default=False)
    allow_connection_add = models.BooleanField("接続追加許可", default=True)
    asn = models.IntegerField("ASN", default=0, null=True, blank=True)
    ave_upstream = models.IntegerField("平均アップロード帯域幅", default=10)
    max_upstream = models.IntegerField("最大アップロード帯域幅", default=20)
    ave_downstream = models.IntegerField("平均ダウンロード帯域幅", default=10)
    max_downstream = models.IntegerField("最大ダウンロード帯域幅", default=20)
    max_bandwidth_as = models.CharField("最大帯域幅AS", default="", blank=True, max_length=255)
    start_at = models.DateTimeField("開通日", null=True, blank=True)
    end_at = models.DateTimeField("解約日", null=True, blank=True)
    user_comment = MediumTextField("ユーザコメント", default="", blank=True)
    admin_comment = MediumTextField("管理者コメント", default="", blank=True)

    objects = ServiceManager()

    def __str__(self):
        return "%s-%s%s" % (self.group.id, self.service_type, str(self.service_number).zfill(3),)


CONNECTION_EIP = "EIP"
CONNECTION_GRE = "GRE"
CONNECTION_IPT = "IPT"
CONNECTION_CC = "CC0"
CONNECTION_ETC = "ETC"

CONNECTION_TYPE_CHOICES = (
    (CONNECTION_EIP, "EtherIP Tunnel"),
    (CONNECTION_GRE, "GRE Tunnel"),
    (CONNECTION_IPT, "IPT Tunnel"),
    (CONNECTION_CC, "Cross Connect"),
    (CONNECTION_ETC, "ETC"),
)

NTT_TYPE1 = "type-1"
NTT_TYPE2 = "type-2"
NTT_TYPE3 = "type-3"
NTT_TYPE4 = "type-4"
NTT_TYPE5 = "type-5"
NTT_TYPE6 = "etc"

NTT_CHOICES = (
    (NTT_TYPE1, "はい（IPoEによりIPv6インターネットへ接続可能）"),
    (NTT_TYPE2, "はい（IPoEによりIPv6インターネットへ接続不可）"),
    (NTT_TYPE3, "はい（フレッツv6オプションの契約なし）"),
    (NTT_TYPE4, "いいえ（フレッツ以外でインターネットに接続可能）"),
    (NTT_TYPE5, "いいえ（IPv6でのインターネット接続不可）"),
    (NTT_TYPE6, "etc"),
)

ROUTE_FULL_ROUTE = "full_route"
ROUTE_DEFAULT_ROUTE = "default_route"
ROUTE_ETC = "full_route"

ROUTE_CHOICES = (
    (ROUTE_FULL_ROUTE, "Full Route"),
    (ROUTE_DEFAULT_ROUTE, "Default Route"),
    (ROUTE_ETC, "Etc"),
)

HOPE_LOCATION_EAST_JAPAN = "east_japan"
HOPE_LOCATION_WEST_JAPAN = "west_japan"
HOPE_LOCATION_ANYWHERE = "anywhere"
HOPE_LOCATION_CHOICES = (
    (HOPE_LOCATION_EAST_JAPAN, "東日本"),
    (HOPE_LOCATION_WEST_JAPAN, "西日本"),
    (HOPE_LOCATION_ANYWHERE, "どちらでも"),
)


class Connection(models.Model):
    class Meta:
        ordering = ("id",)
        verbose_name = "Connection"
        verbose_name_plural = "Connections"

    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, related_name="ConnectionService", null=True, blank=True)
    connection_type = models.IntegerField("サービスタイプ", default=CONNECTION_EIP, choices=CONNECTION_TYPE_CHOICES)
    connection_number = models.IntegerField("接続番号", default=0)
    connection_comment = models.IntegerField("接続情報コメント", default=0, blank=True)
    is_active = models.BooleanField("有効", default=True)
    is_open = models.BooleanField("開通", default=False)
    tunnel_ip = models.ForeignKey(TunnelIP, on_delete=models.CASCADE, related_name="ConnectionTunnelIP", max_length=255)
    hope_location = models.CharField("接続希望場所", default=HOPE_LOCATION_ANYWHERE, choices=HOPE_LOCATION_CHOICES, max_length=255)
    term_location = models.CharField("接続終端場所", default="", blank=True, max_length=255)
    ntt_type = models.CharField("NTT接続タイプ", default=NTT_TYPE1, choices=NTT_CHOICES, max_length=255)
    ntt_comment = models.CharField("NTT接続コメント", default="", blank=True, max_length=255)
    ipv4_route = models.CharField("IPv4 Route", default=ROUTE_FULL_ROUTE, choices=ROUTE_CHOICES, max_length=255)
    ipv4_comment = models.CharField("IPv4コメント", default="", blank=True, max_length=255)
    ipv6_route = models.CharField("IPv6 Route", default=ROUTE_FULL_ROUTE, choices=ROUTE_CHOICES, max_length=255)
    ipv6_comment = models.CharField("IPv6コメント", default="", blank=True, max_length=255)
    is_monitor = models.BooleanField("監視の有無", default=False)
    link_v4_our = models.GenericIPAddressField("IPv4接続(HomeNOC側)", null=True, blank=True)
    link_v4_your = models.GenericIPAddressField("IPv4(貴団体側)", null=True, blank=True)
    link_v6_our = models.GenericIPAddressField("IPv6接続(HomeNOC側)", null=True, blank=True)
    link_v6_your = models.GenericIPAddressField("IPv6(貴団体側)", null=True, blank=True)
    term_ip = models.GenericIPAddressField("終端先IP", null=True, blank=True)
    start_at = models.DateTimeField("開通日", null=True, blank=True)
    end_at = models.DateTimeField("解約日", null=True, blank=True)
    user_comment = MediumTextField("ユーザコメント", default="", blank=True)
    admin_comment = MediumTextField("管理者コメント", default="", blank=True)

    def __str__(self):
        return "%s-%s%s-%s%s" % (
            self.service.group.id,
            self.service.service_type,
            str(self.service.service_number).zfill(3),
            self.connection_type,
            str(self.connection_number).zfill(3),
        )
