from django.contrib import admin

from .models import Service, Connection


@admin.register(Service)
class Service(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('is_active', 'is_pass', 'allow_connection_add')}),
        ('service', {'fields': ('service_type', 'service_number', 'start_at', 'end_at', 'asn')}),
        ('bandwidth',
         {'fields': ('ave_upstream', 'max_upstream', 'ave_downstream', 'max_downstream', 'max_bandwidth_as')}),
        ('comment', {'fields': ('user_comment', 'admin_comment')}),
        ('Important dates', {'fields': ('created_at', 'updated_at',)}),
    )
    list_display = ('id', 'is_active', 'is_pass', 'group', 'start_at', 'end_at')
    list_filter = ('end_at',)
    search_fields = ('end_at', 'is_active', 'service_type')


@admin.register(Connection)
class Connection(admin.ModelAdmin):
    fieldsets = (
        (None,
         {'fields': ('is_active', 'is_open', 'service', 'connection_type', 'connection_number', 'connection_comment')}),
        ('入力情報',
         {'fields': ('ntt_type', 'ntt_comment', 'ipv4_route', 'ipv4_comment', 'ipv6_route', 'ipv6_comment',
                     'start_at', 'end_at', 'is_monitor', 'term_location', 'hope_location')}),
        ('Info', {'fields': (
            'tunnel_ip', 'term_ip', 'link_v4_our', 'link_v4_your', 'link_v6_our', 'link_v6_your')}),
        ('comment', {'fields': ('user_comment', 'admin_comment')}),
        ('Important dates', {'fields': ('created_at', 'updated_at',)}),
    )
    list_display = ('id', 'is_active', 'is_open', 'service', 'start_at', 'end_at')
    list_filter = ('is_active', 'is_open', 'start_at', 'end_at',)
    search_fields = ('is_active', 'service_type')
