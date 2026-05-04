import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steamlike_backend.settings")
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS = ['*']
settings.DEBUG = True

import os
os.environ["MAILEROO_API_KEY"] = "fake_api_key_for_testing"
os.environ["MAILEROO_FROM_EMAIL"] = "test@steamlike.com"

from django.test import Client
from django.urls import reverse
from unittest.mock import patch
from steamlike_backend.services.email_service import ExternalServiceUnavailable, ExternalServiceError

def run_evidences():
    client = Client()
    print("="*50)
    print("EVIDENCIAS UA8")
    print("="*50)

    # ---------------------------------------------------------
    # EJERCICIO 2: POST /api/debug/email/test/
    # ---------------------------------------------------------
    print("\n--- EJERCICIO 2: PRUEBAS DEL ENDPOINT DEBUG ---")
    url_debug = '/api/debug/email/test/'
    
    # 1. Petición correcta
    with patch('steamlike_backend.services.email_service.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}
        
        data = {"to": "test@example.com", "subject": "Test", "text": "Hello"}
        resp = client.post(url_debug, data=json.dumps(data), content_type="application/json")
        try: body = resp.json()
        except: body = resp.content.decode()
        print(f"1. Petición correcta -> Status: {resp.status_code}, Body: {body}")

    # 2. Inválidas: JSON vacío
    resp = client.post(url_debug, data=json.dumps({}), content_type="application/json")
    try: body = resp.json()
    except: body = resp.content.decode()
    print(f"2a. Inválida (JSON vacío) -> Status: {resp.status_code}, Body: {body}")

    # 2. Inválidas: Falta to
    data = {"subject": "Test", "text": "Hello"}
    resp = client.post(url_debug, data=json.dumps(data), content_type="application/json")
    try: body = resp.json()
    except: body = resp.content.decode()
    print(f"2b. Inválida (Falta 'to') -> Status: {resp.status_code}, Body: {body}")

    # 2. Inválidas: 'to' no es string
    data = {"to": 123, "subject": "Test", "text": "Hello"}
    resp = client.post(url_debug, data=json.dumps(data), content_type="application/json")
    try: body = resp.json()
    except: body = resp.content.decode()
    print(f"2c. Inválida ('to' no string) -> Status: {resp.status_code}, Body: {body}")

    # 3. Forzar 503
    with patch('steamlike_backend.services.email_service.requests.post') as mock_post:
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Timeout forced")
        
        data = {"to": "test@example.com", "subject": "Test", "text": "Hello"}
        resp = client.post(url_debug, data=json.dumps(data), content_type="application/json")
        try: body = resp.json()
        except: body = resp.content.decode()
        print(f"3. Forzar 503 (Timeout) -> Status: {resp.status_code}, Body: {body}")

    # 4. Forzar 502
    with patch('steamlike_backend.services.email_service.requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        
        data = {"to": "test@example.com", "subject": "Test", "text": "Hello"}
        resp = client.post(url_debug, data=json.dumps(data), content_type="application/json")
        try: body = resp.json()
        except: body = resp.content.decode()
        print(f"4. Forzar 502 (Error proveedor) -> Status: {resp.status_code}, Body: {body}")

    # ---------------------------------------------------------
    # EJERCICIO 5: REGISTRO CON EMAIL INTEGRADO
    # ---------------------------------------------------------
    print("\n--- EJERCICIO 5: PRUEBAS DE REGISTRO INTEGRADO ---")
    
    # Limpiamos base de datos para no colisionar
    from django.contrib.auth.models import User
    User.objects.all().delete()
    
    url_register = reverse('register')
    
    # 1. Registro correcto y envío OK
    with patch('steamlike_backend.services.email_service.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}
        
        data = {"username": "user_ok", "password": "password123", "email": "user_ok@example.com"}
        resp = client.post(url_register, data=json.dumps(data), content_type="application/json")
        try: body = resp.json()
        except: body = resp.content.decode()
        print(f"1. Registro OK (Email OK) -> Status: {resp.status_code}, Body: {body}")

    # 2. Registro correcto forzando fallo (502 o 503)
    with patch('steamlike_backend.services.email_service.requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        
        data = {"username": "user_fail", "password": "password123", "email": "user_fail@example.com"}
        resp = client.post(url_register, data=json.dumps(data), content_type="application/json")
        try: body = resp.json()
        except: body = resp.content.decode()
        print(f"2. Registro OK (Email Fail 502) -> Status: {resp.status_code}, Body: {body}")

if __name__ == "__main__":
    run_evidences()
