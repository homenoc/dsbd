from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from custom_auth.models import Group, TOTPDevice, User, UserActivateToken
from ip.models import JPNICUser
from service.models import Service


class TermInlineUserAdmin(admin.TabularInline):
    model = User.groups.through
    extra = 0


class TermInlineGroupAdmin(admin.TabularInline):
    model = Group.users.through
    extra = 0


class TermInlineGroupServiceAdmin(admin.TabularInline):
    model = Service
    extra = 0
    fields = ("service_code", "service_type", "service_number", "is_active", "is_pass")
    readonly_fields = ("service_code", "service_type", "service_number", "is_active", "is_pass")

    def service_code(self, obj):
        # 管理ページの編集ページへのリンクを生成
        url = reverse("admin:service_service_change", args=[obj.id])
        return format_html('<a href="{}" target="__blank__">{}</a>', url, obj.service_code)

    service_code.short_description = "ServiceCode"


class TermInlineGroupJPNICAdmin(admin.TabularInline):
    model = JPNICUser
    extra = 0
    fields = ("id_link", "jpnic_handle", "name", "org", "is_pass")
    readonly_fields = ("id_link", "jpnic_handle", "name", "org", "is_pass")

    def id_link(self, obj):
        # 管理ページの編集ページへのリンクを生成
        url = reverse("admin:ip_jpnicuser_change", args=[obj.id])
        return format_html('<a href="{}" target="__blank__">{}</a>', url, obj.id)

    id_link.short_description = "ID"


@admin.register(User)
class User(SimpleHistoryAdmin):
    fieldsets = (
        (None, {"fields": ("username", "username_jp", "password")}),
        ("Personal info", {"fields": ("email",)}),
        ("Flags", {"fields": ("is_active", "is_staff", "allow_group_add")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    list_display = (
        "username",
        "username_jp",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "is_staff",
        "is_active",
    )
    search_fields = ("username", "username_jp", "email")
    readonly_fields = (
        "last_login",
        "created_at",
        "updated_at",
    )

    inlines = (TermInlineUserAdmin,)

    def get_groups(self, obj):
        return "\n".join([p.groups for p in obj.group.all()])


@admin.register(Group)
class Group(SimpleHistoryAdmin):
    fieldsets = (
        (None, {"fields": ("name", "name_jp", "allow_service_add", "allow_jpnic_add", "is_pass", "comment")}),
        ("Membership", {"fields": ("membership_type", "membership_expired_at")}),
        ("Question", {"fields": ("agree", "question")}),
        ("Stripe", {"fields": ("stripe_customer_id", "stripe_subscription_id")}),
        (
            "Personal info",
            {
                "fields": (
                    "postcode",
                    "address",
                    "address_jp",
                    "phone",
                    "country",
                    "contract_type",
                )
            },
        ),
    )
    list_display = (
        "name",
        "name_jp",
        "membership_type",
        "membership_expired_at",
    )
    list_filter = (
        "membership_type",
        "is_pass",
        "allow_service_add",
    )
    search_fields = (
        "name",
        "name_jp",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = (
        TermInlineGroupAdmin,
        TermInlineGroupServiceAdmin,
        TermInlineGroupJPNICAdmin,
    )


@admin.register(UserActivateToken)
class UserActivateToken(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("user", "token", "expired_at", "is_used")}),
        ("Important dates", {"fields": ("created_at",)}),
    )
    list_display = ("user", "token", "expired_at", "is_used")
    list_filter = ("is_used",)
    search_fields = ("user", "token", "expired_at", "is_used")


@admin.register(TOTPDevice)
class TOTPDevice(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("title", "is_active", "user", "secret")}),
        ("Important dates", {"fields": ("created_at",)}),
    )
    list_display = (
        "id",
        "is_active",
        "title",
        "user",
    )
    list_filter = ("is_active",)
    search_fields = (
        "id",
        "is_active",
        "title",
    )
