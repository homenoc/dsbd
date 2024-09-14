from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import TunnelIP, TunnelRouter


class TermInlineRouterTunnelIPAdmin(admin.TabularInline):
    model = TunnelIP
    extra = 0
    fields = ("id_link", "is_active", "name", "ip_address", "comment")
    readonly_fields = ("id_link", "comment")

    def id_link(self, obj):
        # 管理ページの編集ページへのリンクを生成
        url = reverse("admin:router_tunnelip_change", args=[obj.id])
        return format_html('<a href="{}" target="__blank__">{}</a>', url, obj.id)

    id_link.short_description = "ID"


@admin.register(TunnelRouter)
class Router(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("is_active", "noc", "hostname")}),
        ("comment", {"fields": ("comment",)}),
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
    list_display = ("id", "is_active", "noc", "hostname")
    list_filter = ("is_active",)
    search_fields = ("is_active", "hostname")
    inlines = [
        TermInlineRouterTunnelIPAdmin,
    ]


@admin.register(TunnelIP)
class TunnelIP(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("is_active", "name", "tunnel_router", "ip_address")}),
        ("comment", {"fields": ("comment",)}),
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
    list_display = ("id", "is_active", "name", "tunnel_router", "ip_address")
    list_filter = ("is_active",)
    search_fields = ("is_active", "ip_address")
