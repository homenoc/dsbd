from django.contrib import admin
from custom_auth.models import User, Group, UserActivateToken


class TermInlineUserAdmin(admin.TabularInline):
    model = User.groups.through
    extra = 1


@admin.register(User)
class User(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ('username', 'username_jp', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Flags', {'fields': ('is_active', 'is_staff', 'allow_group_add')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    list_display = ('username', 'username_jp',)
    list_filter = ('is_staff', 'is_active',)
    search_fields = ('username', 'username_jp', 'email')
    readonly_fields = ('last_login', 'created_at', 'updated_at',)

    inlines = (TermInlineUserAdmin,)

    def get_groups(self, obj):
        return "\n".join([p.groups for p in obj.group.all()])


@admin.register(Group)
class Group(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ('name', 'name_jp', 'allow_service_add', 'is_pass', 'comment')}),
        ('Membership', {'fields': ('membership_type', 'membership_expired_at')}),
        ('Question', {'fields': ('agree', 'question')}),
        ('Stripe', {'fields': ('stripe_customer_id', 'stripe_subscription_id')}),
        ('Personal info', {'fields': ('postcode', 'address', 'address_jp', 'phone', 'country', 'contract_type',)}),
    )
    list_display = ('name', 'name_jp', 'membership_type', 'membership_expired_at',)
    list_filter = ('membership_type',)
    search_fields = ('name', 'name_jp',)
    readonly_fields = ('created_at', 'updated_at',)


@admin.register(UserActivateToken)
class UserActivateToken(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ('user', 'token', 'expired_at', 'is_used')}),
        ('Important dates', {'fields': ('created_at',)}),
    )
    list_display = ('user', 'token', 'expired_at', 'is_used')
    search_fields = ('user', 'token', 'expired_at', 'is_used')
