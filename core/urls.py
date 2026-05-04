from django.urls import path
from .views import debug_email_test, debug_clear_users

urlpatterns = [
    path('debug/email/test/', debug_email_test, name='debug_email_test'),
    path('debug/clear-users/', debug_clear_users, name='debug_clear_users'),
]
