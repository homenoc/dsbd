from django.urls import path

from . import views

app_name = "custom_auth_group"
urlpatterns = [
    path("", views.list_groups, name="index"),
    path("add/", views.add_group, name="add"),
    path("edit/<int:group_id>", views.edit_group, name="edit"),
    path("permission/<int:group_id>", views.group_permission, name="permission"),
    path("<int:group_id>/payment", views.group_payment, name="payment"),
]
