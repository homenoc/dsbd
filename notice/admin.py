from django.contrib import admin

from notice.models import Notice


@admin.register(Notice)
class Notice(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("created_at", "start_at", "end_at", "is_active")}),
        ("info", {"fields": ("type1", "title", "body")}),
        ("Flags", {"fields": ("is_important", "is_fail", "is_info")}),
    )
    list_display = (
        "id",
        "created_at",
        "start_at",
        "end_at",
        "type1",
        "is_active",
        "title",
        "is_important",
        "is_fail",
        "is_info",
    )
    list_filter = ("end_at",)
    search_fields = ("end_at", "is_important", "is_fail", "is_info")
