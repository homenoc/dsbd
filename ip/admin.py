from django.contrib import admin

from .models import IP, JPNICUser


class TermInlineIPAdmin(admin.TabularInline):
    model = IP.jpnic_user.through
    extra = 1


class TermInlineJPNICUserAdmin(admin.TabularInline):
    model = JPNICUser.ip.through
    extra = 1


@admin.register(IP)
class IP(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('is_active', 'service',)}),
        ('ip', {'fields': ('ip_address', 'subnet', 'start_at', 'end_at', 'plan', 'use_case')}),
        ('Important dates', {'fields': ('created_at', 'updated_at',)}),
    )
    list_display = ('id', 'is_active', 'service', 'ip_address', 'subnet', 'start_at', 'end_at')
    list_filter = ('is_active', 'end_at',)
    search_fields = ('ip_address',)

    inlines = (TermInlineIPAdmin,)


@admin.register(JPNICUser)
class JPNICUser(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('group', 'is_active',)}),
        ('Common', {'fields': ('hidden', 'handle_type', 'jpnic_handle')}),
        ('Personal info', {'fields': (
            'name', 'name_jp', 'email', 'org', 'org_en', 'postcode', 'address', 'address_jp',
            'dept', 'dept_en', 'title', 'title_en', 'tel', 'fax', 'country')}),
        ('Important dates', {'fields': ('created_at', 'updated_at',)}),
    )
    list_display = ('id', 'is_active', 'group', 'jpnic_handle', 'name', 'org')
    list_filter = ('is_active', 'group')
    search_fields = ('name', 'group', 'org')

    inlines = (TermInlineJPNICUserAdmin,)
