import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from .models import LibraryEntry

class LibraryAPIExcercisesTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Creamos un usuario principal
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.list_create_url = reverse('entries-list-create')
        
        # Mokeamos el acceso a la API externa de catalog para que siempre devuelva válido
        self.patcher = patch('catalog.utils.check_game_exists', return_value=(True, None))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    # ==========================================
    # EJERCICIO 1: POST /api/auth/register/
    # ==========================================
    def test_ex1_register_valid(self):
        data = {"username": "newuser", "password": "newpassword123"}
        response = self.client.post(reverse('register'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        resp_json = response.json()
        self.assertIn("id", resp_json)
        self.assertEqual(resp_json["username"], "newuser")
        self.assertNotIn("password", resp_json)

    def test_ex1_register_invalid_empty_json(self):
        response = self.client.post(reverse('register'), data=json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")

    def test_ex1_register_invalid_missing_fields(self):
        data = {"username": "missingpass"}
        response = self.client.post(reverse('register'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")

    def test_ex1_register_invalid_short_password(self):
        data = {"username": "shortpassuser", "password": "123"}
        response = self.client.post(reverse('register'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")

    def test_ex1_register_invalid_duplicate_username(self):
        data = {"username": "testuser", "password": "anotherpassword"}
        response = self.client.post(reverse('register'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")


    # ==========================================
    # EJERCICIO 2: POST /api/auth/login/
    # ==========================================
    def test_ex2_login_valid(self):
        data = {"username": "testuser", "password": "password123"}
        response = self.client.post(reverse('login'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_ex2_login_invalid_credentials(self):
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(reverse('login'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "unauthorized")

    def test_ex2_login_invalid_validation(self):
        response = self.client.post(reverse('login'), data=json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")


    # ==========================================
    # EJERCICIO 3: GET /api/users/me/
    # ==========================================
    def test_ex3_me_unauthorized(self):
        # Sin hacer login
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "unauthorized")

    def test_ex3_me_authorized(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        self.assertEqual(response.json()["username"], "testuser")


    # ==========================================
    # EJERCICIO 4: GET /api/library/entries/
    # ==========================================
    def test_ex4_list_unauthorized(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "unauthorized")

    def test_ex4_list_authorized_and_isolation(self):
        # Crear entrada para usuario A (testuser)
        LibraryEntry.objects.create(user=self.user, external_game_id="gameA", status="playing", hours_played=10)
        
        # Crear entrada para usuario B
        user_b = User.objects.create_user(username="userB", password="password123")
        LibraryEntry.objects.create(user=user_b, external_game_id="gameB", status="wishlist", hours_played=0)
        
        # Autenticar como usuario A
        self.client.force_login(self.user)
        response = self.client.get(self.list_create_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["external_game_id"], "gameA")


    # ==========================================
    # EJERCICIO 5: GET /api/library/entries/{id}/
    # ==========================================
    def test_ex5_detail_unauthorized(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="game_detail", status="playing", hours_played=1)
        detail_url = reverse('entry-detail-update', args=[e.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "unauthorized")

    def test_ex5_detail_authorized_own(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="game_own", status="playing", hours_played=1)
        detail_url = reverse('entry-detail-update', args=[e.id])
        self.client.force_login(self.user)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["external_game_id"], "game_own")

    def test_ex5_detail_authorized_other(self):
        user_b = User.objects.create_user(username="userB", password="password123")
        e_b = LibraryEntry.objects.create(user=user_b, external_game_id="game_other", status="playing", hours_played=1)
        detail_url = reverse('entry-detail-update', args=[e_b.id])
        
        self.client.force_login(self.user)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "not_found")


    # ==========================================
    # EJERCICIO 6: POST /api/library/entries/
    # ==========================================
    def test_ex6_create_unauthorized(self):
        data = {"external_game_id": "game_new", "status": "playing", "hours_played": 5}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "unauthorized")

    def test_ex6_create_authorized_and_isolation(self):
        self.client.force_login(self.user)
        data = {"external_game_id": "game_new", "status": "playing", "hours_played": 5}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        
        # Verificar que el usuario B NO ve esta entrada en su listado
        user_b = User.objects.create_user(username="userB", password="password123")
        self.client.force_login(user_b)
        response_b = self.client.get(self.list_create_url)
        self.assertEqual(response_b.status_code, 200)
        self.assertEqual(len(response_b.json()), 0)
