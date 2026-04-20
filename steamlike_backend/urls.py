from django.contrib import admin
from django.urls import path, include
from library.views import health
from library import auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", auth_views.register),
    path("api/auth/login/", auth_views.login_view),
    path("api/users/me/", auth_views.me),
    path("api/library/", include("library.urls")),
    path("api/health/", health)
]
