from django.urls import path, include

from . import views

app_name = "custom_admin"
urlpatterns = [
    path("", views.index, name="index"),
    path("ticket", views.ticket_list, name="ticket_list"),
    path("ticket/<int:ticket_id>/chat/", views.chat, name="chat"),
]
