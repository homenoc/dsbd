from django.contrib import admin

from .models import NOC


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
