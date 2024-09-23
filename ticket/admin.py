from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from ticket.models import Chat, Ticket


@admin.register(Ticket)
class Ticket(SimpleHistoryAdmin):
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("created_at", "updated_at", "user", "group")}),
        ("info", {"fields": ("title", "body")}),
        ("Flags", {"fields": ("from_admin", "is_template", "is_solved", "is_approve", "is_reject")}),
    )
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "user",
        "group",
        "title",
        "is_solved",
    )
    list_filter = ("is_solved",)
    search_fields = ("user", "group", "from_admin", "is_solved", "is_approve", "is_reject")


@admin.register(Chat)
class Chat(SimpleHistoryAdmin):
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("created_at", "user", "group", "ticket")}),
        ("info", {"fields": ("body",)}),
        ("Flags", {"fields": ("is_admin",)}),
    )
    list_display = ("id", "created_at", "user", "group", "ticket", "is_admin")
    list_filter = ("group",)
    search_fields = ("created_at", "user", "group", "ticket")
