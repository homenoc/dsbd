"""
URL configuration for dsbd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from dsbd import views
from django.conf import settings

urlpatterns = [
    path("", views.index, name="index"),
    path("menu", views.menu, name="menu"),
    path("sign_in/", views.sign_in, name="sign_in"),
    path("sign_out/", views.sign_out, name="sign_out"),
    path("sign_up/", views.sign_up, name="sign_up"),
    path("sign_up/done", views.sign_up_done, name="sign_up_done"),
    path('forget/', views.PasswordReset.as_view(), name='password_reset'),
    path('forget/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('forget/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('forget/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('activate/<uuid:activate_token>/', views.activate_user, name='activate_user'),
    path("group/", include("custom_auth.group_urls")),
    path("profile/", include("custom_auth.urls")),
    path("ticket/", include("ticket.urls")),
    path("service/", include("service.urls")),
    path("feedback/", views.feedback, name="feedback"),
]

if settings.ADMIN_MODE:
    from django.contrib import admin

    urlpatterns += [
        path('admin/custom/', include("custom_admin.urls")),
        path('admin/login/', views.admin_sign_in, name='admin_sign_in'),
        path("admin/", admin.site.urls),
    ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
