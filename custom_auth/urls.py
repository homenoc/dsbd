from django.urls import path, include

from . import views

app_name = "custom_auth"
urlpatterns = [
    path("", views.index, name="index"),
    path("change/password", views.change_password, name="change_password"),
    path("two_auth", views.list_two_auth, name="list_two_auth"),
    path("two_auth/add", views.add_two_auth, name="add_two_auth"),
]
