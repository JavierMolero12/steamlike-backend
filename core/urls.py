from django.urls import path
from .views import debug_email_test

urlpatterns = [
    path('debug/email/test/', debug_email_test, name='debug_email_test'),
]
