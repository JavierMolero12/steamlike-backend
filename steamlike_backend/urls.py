from django.contrib import admin
from django.urls import path, include
from library.views import health
from library import auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticación
    path("api/auth/register/", auth_views.register, name="register"),
    path("api/auth/login/", auth_views.login_view, name="login"),
    path("api/auth/logout/", auth_views.logout_view, name="logout"),
    
    # Usuario actual
    path("api/users/me/", auth_views.manage_me, name="me"), # GET (me) y DELETE (borrado)
    path("api/users/me/password/", auth_views.change_password, name="change-password"),
    
    # Biblioteca y Salud
    path("api/library/", include("library.urls")),
    path("api/health/", health, name="health"),
    path("health/", health)
]
