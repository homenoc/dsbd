from django.contrib import admin

from .models import TunnelRouter, TunnelIP


@admin.register(TunnelRouter)
class Router(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('is_active', 'noc', 'hostname')}),
        ('comment', {'fields': ('comment',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at',)}),
    )
    list_display = ('id', 'is_active', 'noc', 'hostname')
    list_filter = ('is_active',)
    search_fields = ('is_active', 'hostname')


@admin.register(TunnelIP)
class TunnelIP(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('is_active', 'tunnel_router', 'ip_address')}),
        ('comment', {'fields': ('comment',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at',)}),
    )
    list_display = ('id', 'is_active', 'tunnel_router', 'ip_address')
    list_filter = ('is_active',)
    search_fields = ('is_active', 'ip_address')
