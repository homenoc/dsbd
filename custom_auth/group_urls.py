from django.urls import path, include

from . import views
from django.contrib.auth import views as auth_views

app_name = "custom_auth_group"
urlpatterns = [
    path("", views.list_groups, name="index"),
]
