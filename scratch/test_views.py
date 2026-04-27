import os
import django
from django.test import Client
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steamlike_backend.settings')
django.setup()

from django.contrib.auth.models import User

# Aseguramos un usuario de prueba
user, _ = User.objects.get_or_create(username='test_catalog', email='test@example.com')
user.set_password('1234')
user.save()

client = Client()
client.force_login(user)

# Crear con un ID inválido "no_existe_este_juego_123"
response = client.post(
    '/api/library/entries/',
    data=json.dumps({"external_game_id": "no_existe_este_juego_123", "status": "playing", "hours_played": 10}),
    content_type='application/json'
)

print(f"Status: {response.status_code}")
print(response.content.decode())

# Crear con ID válido "128"
response2 = client.post(
    '/api/library/entries/',
    data=json.dumps({"external_game_id": "128", "status": "playing", "hours_played": 10}),
    content_type='application/json'
)
print(f"Status 2: {response2.status_code}")
print(response2.content.decode())
