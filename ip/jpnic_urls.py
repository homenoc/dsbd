from django.urls import path

from . import views

app_name = "jpnic"
urlpatterns = [
    path("", views.jpnic_index, name="jpnic_index"),
    path("add/", views.jpnic_add, name="jpnic_add"),
    path("<int:jpnic_id>/edit", views.jpnic_edit, name="jpnic_edit"),
]
