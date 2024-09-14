from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from ip.models import IP

from .models import Connection, Service


class TermInlineServiceIPAdmin(admin.TabularInline):
    model = IP
    extra = 0
    fields = ("id_link", "ip_address", "subnet", "is_active", "is_pass")
    readonly_fields = ("id_link",)

    def id_link(self, obj):
        # 管理ページの編集ページへのリンクを生成
        url = reverse("admin:ip_ip_change", args=[obj.id])
        return format_html('<a href="{}" target="__blank__">{}</a>', url, obj.id)

    id_link.short_description = "ID"


class TermInlineServiceConnectionAdmin(admin.TabularInline):
    model = Connection
    extra = 0
    fields = ("id_link", "is_active", "is_open")
    readonly_fields = ("id_link",)

    def id_link(self, obj):
        # 管理ページの編集ページへのリンクを生成
        url = reverse("admin:service_connection_change", args=[obj.id])
        return format_html('<a href="{}" target="__blank__">{}</a>', url, obj.service_code)

    id_link.short_description = "ID"


@admin.register(Service)
class Service(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("is_active", "is_pass", "allow_connection_add", "group")}),
        ("service", {"fields": ("service_type", "service_number", "start_at", "end_at", "asn")}),
        (
            "bandwidth",
            {"fields": ("ave_upstream", "max_upstream", "ave_downstream", "max_downstream", "max_bandwidth_as")},
        ),
        ("comment", {"fields": ("user_comment", "admin_comment")}),
        (
            "Important dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    list_display = ("service_code", "is_active", "is_pass", "group", "start_at", "end_at")
    list_filter = ("end_at",)
    search_fields = ("service_code", "is_active", "service_type")
    inlines = [
        TermInlineServiceIPAdmin,
        TermInlineServiceConnectionAdmin,
    ]


@admin.register(Connection)
class Connection(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "is_active",
                    "is_open",
                    "service",
                    "connection_type",
                    "connection_number",
                    "connection_comment",
                )
            },
        ),
        (
            "入力情報",
            {
                "fields": (
                    "ntt_type",
                    "ntt_comment",
                    "ipv4_route",
                    "ipv4_route_comment",
                    "ipv6_route",
                    "ipv6_route_comment",
                    "start_at",
                    "end_at",
                    "is_monitor",
                    "term_location",
                    "hope_location",
                )
            },
        ),
        ("Info", {"fields": ("tunnel_ip", "term_ip", "link_v4_our", "link_v4_your", "link_v6_our", "link_v6_your")}),
        ("comment", {"fields": ("user_comment", "admin_comment")}),
        (
            "Important dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    list_display = ("service_code", "is_active", "is_open", "service", "start_at", "end_at")
    list_filter = (
        "is_active",
        "is_open",
        "start_at",
        "end_at",
    )
    search_fields = ("service_code", "is_active", "service_type")
