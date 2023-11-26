from django.urls import path
from . import consumers

urlpatterns = [
    path('ws/ticket/<int:ticket_id>/chat', consumers.ChatConsumer.as_asgi()),
]
