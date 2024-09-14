from django.contrib import admin

from .models import IP, JPNICUser


class TermInlineIPAdmin(admin.TabularInline):
    model = IP.jpnic_user.through
    extra = 0
    readonly_fields = ("created_at", "updated_at", "jpnic_user", "user_type")


class TermInlineJPNICUserAdmin(admin.TabularInline):
    model = JPNICUser.ip.through
    extra = 0


@admin.register(IP)
class IP(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "is_active",
                    "service",
                )
            },
        ),
        ("ip", {"fields": ("ip_address", "subnet", "start_at", "end_at", "ipv4_plan", "use_case")}),
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
    list_display = ("id", "is_active", "is_pass", "service", "ip_address", "subnet", "start_at", "end_at")
    list_filter = (
        "is_active",
        "is_pass",
        "end_at",
    )
    search_fields = ("ip_address",)

    inlines = (TermInlineIPAdmin,)


@admin.register(JPNICUser)
class JPNICUser(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "group",
                    "is_pass",
                )
            },
        ),
        ("Common", {"fields": ("hidden", "handle_type", "jpnic_handle")}),
        (
            "Personal info",
            {
                "fields": (
                    "name",
                    "name_jp",
                    "email",
                    "org",
                    "org_jp",
                    "postcode",
                    "address",
                    "address_jp",
                    "dept",
                    "dept_jp",
                    "title",
                    "title_jp",
                    "tel",
                    "fax",
                    "country",
                )
            },
        ),
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
    list_display = ("id", "is_pass", "group", "jpnic_handle", "name", "org")
    list_filter = ("is_pass", "group")
    search_fields = ("name", "name_jp", "group", "org", "org_jp")

    inlines = (TermInlineJPNICUserAdmin,)
