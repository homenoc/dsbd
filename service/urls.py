from django.urls import path

from . import views

app_name = "services"
urlpatterns = [
    path("", views.service_index, name="index"),
]
