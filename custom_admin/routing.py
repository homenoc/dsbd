from django.urls import path
from . import consumers

urlpatterns = [
    path('ws/admin/custom/ticket/<int:ticket_id>/chat', consumers.AdminChatConsumer.as_asgi()),
]
