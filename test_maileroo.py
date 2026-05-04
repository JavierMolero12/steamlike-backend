import os
import django
from django.conf import settings

# Setup minimal django environment to test the service
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steamlike_backend.settings")
django.setup()

from steamlike_backend.services.email_service import EmailService

# Mock environment variables
os.environ["MAILEROO_API_KEY"] = "5c498a663bd7c893c352a669d715197daff854d4a6ff7d8efd23eaad83b9bbce"
os.environ["MAILEROO_FROM_EMAIL"] = "soporte@991c80f32ce39ele.maileroo.org"
os.environ["MAILEROO_FROM_NAME"] = "Steamlike"

print("Sending email...")
try:
    result = EmailService.send_email(
        to="javichimolero@gmail.com",
        subject="Prueba desde Steamlike",
        text="Hola! Este es un correo de prueba después de arreglar la conexión."
    )
    print("Success:", result)
except Exception as e:
    print("Failed:", type(e), str(e))
