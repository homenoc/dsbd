from django.urls import path

from . import views

app_name = "custom_auth_group"
urlpatterns = [
    path("", views.list_groups, name="index"),
    path("<int:group_id>/", views.list_group, name="list"),
    path("add/", views.add_group, name="add"),
    path("<int:group_id>/edit", views.edit_group, name="edit"),
    path("<int:group_id>/permission", views.group_permission, name="permission"),
    path("<int:group_id>/payment", views.group_payment, name="payment"),
]
