from django.urls import path

from . import views

app_name = "service"
urlpatterns = [
    path("", views.service_index, name="index"),
    path("add/", views.service_add, name="add"),
    path("<int:service_id>/connection/add", views.connection_add, name="connection_add"),
]
