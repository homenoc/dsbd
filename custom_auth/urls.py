from django.urls import path

from . import views

app_name = "custom_auth"
urlpatterns = [
    path("", views.index, name="index"),
    path("password", views.password_change, name="password_change"),
    path("email", views.change_email, name="email_change"),
    path("edit", views.edit_profile, name="edit_profile"),
    path("two_auth", views.list_two_auth, name="list_two_auth"),
    path("two_auth/add", views.add_two_auth, name="add_two_auth"),
]
