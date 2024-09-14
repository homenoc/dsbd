from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from router.models import TunnelRouter

from .models import NOC


class TermInlineNOCRouterAdmin(admin.TabularInline):
    model = TunnelRouter
    extra = 0
    fields = ("id_link", "is_active", "hostname", "comment")
    readonly_fields = ("id_link", "comment")

    def id_link(self, obj):
        # 管理ページの編集ページへのリンクを生成
        url = reverse("admin:router_tunnelrouter_change", args=[obj.id])
        return format_html('<a href="{}" target="__blank__">{}</a>', url, obj.id)

    id_link.short_description = "ID"


@admin.register(NOC)
class NOC(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "is_active",
                    "location",
                    "bandwidth",
                )
            },
        ),
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
    list_display = ("id", "name", "is_active", "location", "bandwidth")
    list_filter = ("is_active",)
    search_fields = ("name",)
    inlines = [
        TermInlineNOCRouterAdmin,
    ]
