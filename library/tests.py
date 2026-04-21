import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import LibraryEntry

class LibraryAPIExcercisesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)
        self.list_create_url = reverse('entries-list-create')

    # Ejercicio 1 Tests (POST)
    def test_ex1_post_valid_entry(self): # 1 ejemplo correcto (201)
        data = {"external_game_id": "game_1", "status": "playing", "hours_played": 10}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        resp_data = response.json()
        self.assertEqual(resp_data["external_game_id"], "game_1")
        self.assertEqual(resp_data["status"], "playing")
        self.assertEqual(resp_data["hours_played"], 10)
        self.assertIn("id", resp_data)

    def test_ex1_post_invalid_status_type(self): # status no sea string
        data = {"external_game_id": "game_2", "status": 123, "hours_played": 0}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")

    def test_ex1_post_invalid_status_value(self): # status no esté en los valores permitidos
        data = {"external_game_id": "game_2", "status": "finished", "hours_played": 0}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_ex1_post_invalid_hours_played_type(self): # hours_played no sea integer
        data = {"external_game_id": "game_2", "status": "completed", "hours_played": "10"}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_ex1_post_invalid_hours_played_value(self): # hours_played < 0
        data = {"external_game_id": "game_2", "status": "completed", "hours_played": -5}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_ex1_post_empty_body(self): # body vacío
        response = self.client.post(self.list_create_url, data=json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    # Ejercicio 3 Tests (Duplicate)
    def test_ex3_duplicate_entry(self):
        # 1 creación correcta -> 201
        data = {"external_game_id": "duplicate_id", "status": "wishlist", "hours_played": 0}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        
        # 1 intento duplicado -> 400
        response2 = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.json()["error"], "duplicate_entry")
        self.assertEqual(response2.json()["details"], {"external_game_id": "duplicate"})

    # Ejercicio 4 Tests (List and Detail)
    def test_ex4_list_and_detail(self):
        # Crear 2 entradas
        e1 = LibraryEntry.objects.create(user=self.user, external_game_id="g1", status="wishlist", hours_played=0)
        e2 = LibraryEntry.objects.create(user=self.user, external_game_id="g2", status="playing", hours_played=20)
        
        # Probar listado (200)
        response_list = self.client.get(self.list_create_url)
        self.assertEqual(response_list.status_code, 200)
        self.assertEqual(len(response_list.json()), 2)
        
        # Probar detalle existente (200)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        response_detail = self.client.get(detail_url)
        self.assertEqual(response_detail.status_code, 200)
        self.assertEqual(response_detail.json()["external_game_id"], "g1")
        
        # Probar detalle inexistente (404)
        not_found_url = reverse('entry-detail-update', args=[9999])
        response_not_found = self.client.get(not_found_url)
        self.assertEqual(response_not_found.status_code, 404)
        self.assertEqual(response_not_found.json()["error"], "not_found")

    # Ejercicio 5 Tests (PATCH)
    def test_ex5_patch_valid(self):
        e1 = LibraryEntry.objects.create(user=self.user, external_game_id="game_patch", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        
        data = {"status": "completed", "hours_played": 50}
        response = self.client.patch(detail_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data["status"], "completed")
        self.assertEqual(resp_data["hours_played"], 50)
        
    def test_ex5_patch_invalid_empty(self):
        e1 = LibraryEntry.objects.create(user=self.user, external_game_id="game_patch_2", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        response = self.client.patch(detail_url, data=json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        
    def test_ex5_patch_invalid_status(self):
        e1 = LibraryEntry.objects.create(user=self.user, external_game_id="game_patch_3", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        response = self.client.patch(detail_url, data=json.dumps({"status": "invalid_status"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        
    def test_ex5_patch_invalid_hours(self):
        e1 = LibraryEntry.objects.create(user=self.user, external_game_id="game_patch_4", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        response = self.client.patch(detail_url, data=json.dumps({"hours_played": -10}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        
    def test_ex5_patch_unknown_field(self):
        e1 = LibraryEntry.objects.create(user=self.user, external_game_id="game_patch_5", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        response = self.client.patch(detail_url, data=json.dumps({"status": "completed", "extra_field": "hello"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("extra_field", response.json()["details"])
        
    def test_ex5_patch_not_found(self):
        detail_url = reverse('entry-detail-update', args=[9999])
        response = self.client.patch(detail_url, data=json.dumps({"status": "completed"}), content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_ex4_multiuser_privacy(self):
        # Usuario A (self.user) crea una entrada
        e_a = LibraryEntry.objects.create(user=self.user, external_game_id="game_a", status="playing", hours_played=5)
        
        # Crear Usuario B
        user_b = User.objects.create_user(username="user_b", password="password123")
        self.client.force_login(user_b)
        
        # Usuario B crea su propia entrada
        e_b = LibraryEntry.objects.create(user=user_b, external_game_id="game_b", status="wishlist", hours_played=0)
        
        # Usuario B intenta listar -> solo debe ver la suya (1 entrada)
        response_list = self.client.get(self.list_create_url)
        self.assertEqual(len(response_list.json()), 1)
        self.assertEqual(response_list.json()[0]["external_game_id"], "game_b")
        
        # Usuario B intenta ver la entrada de A -> debe dar 404
        detail_a_url = reverse('entry-detail-update', args=[e_a.id])
        response_detail = self.client.get(detail_a_url)
        self.assertEqual(response_detail.status_code, 404)
        self.assertEqual(response_detail.json()["error"], "not_found")
        
        # Usuario B intenta modificar la entrada de A -> debe dar 404
        response_patch = self.client.patch(detail_a_url, data=json.dumps({"status": "completed"}), content_type="application/json")
        self.assertEqual(response_patch.status_code, 404)

    # --- NUEVOS TESTS ADICIONALES (Para alcanzar 50) ---

    # Autenticación y Registro (Ejercicios 2 y 3)
    def test_auth_register_duplicate_username(self):
        User.objects.create_user(username="existing", password="password123")
        data = {"username": "existing", "password": "newpassword123"}
        response = self.client.post(reverse('register'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")

    def test_auth_register_short_password(self):
        data = {"username": "newuser", "password": "short"}
        response = self.client.post(reverse('register'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_auth_register_invalid_types(self):
        data = {"username": 123, "password": ["wrong", "type"]}
        response = self.client.post(reverse('register'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_auth_login_invalid_credentials(self):
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(reverse('login'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "unauthorized")

    def test_auth_login_non_existent_user(self):
        data = {"username": "idontbound", "password": "somepassword"}
        response = self.client.post(reverse('login'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_auth_login_missing_username(self):
        data = {"password": "somepassword"}
        response = self.client.post(reverse('login'), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_auth_me_unauthorized(self):
        self.client.logout()
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, 401)

    def test_auth_me_authorized_after_login(self):
        data = {"username": "testuser", "password": "password123"}
        self.client.post(reverse('login'), data=json.dumps(data), content_type="application/json")
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "testuser")

    def test_auth_register_empty_json(self):
        response = self.client.post(reverse('register'), data=json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_auth_login_wrong_json_format(self):
        response = self.client.post(reverse('login'), data="not a json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    # Creación y Duplicados (Ejercicios 1 y 3)
    def test_ex3_independent_duplicates(self):
        # El mismo juego para dos usuarios distintos debe permitirse
        LibraryEntry.objects.create(user=self.user, external_game_id="shared_game", status="wishlist", hours_played=0)
        
        user_b = User.objects.create_user(username="user_b_new", password="password123")
        self.client.force_login(user_b)
        
        data = {"external_game_id": "shared_game", "status": "playing", "hours_played": 5}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_ex1_post_missing_external_id(self):
        data = {"status": "playing", "hours_played": 10}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("external_game_id", response.json()["details"])

    def test_ex1_post_missing_status(self):
        data = {"external_game_id": "g_test", "hours_played": 10}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_ex1_post_missing_hours(self):
        data = {"external_game_id": "g_test", "status": "playing"}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    # Listado, Detalles y Privacidad (Ejercicio 4)
    def test_ex4_list_empty(self):
        LibraryEntry.objects.all().delete()
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_ex4_detail_not_owner(self):
        other_user = User.objects.create_user(username="other", password="password123")
        entry = LibraryEntry.objects.create(user=other_user, external_game_id="other_game", status="playing", hours_played=5)
        detail_url = reverse('entry-detail-update', args=[entry.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)

    def test_ex4_detail_non_existent(self):
        detail_url = reverse('entry-detail-update', args=[99999])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)

    def test_ex4_list_unauthorized(self):
        self.client.logout()
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, 401)

    def test_ex1_post_unauthorized(self):
        self.client.logout()
        data = {"external_game_id": "g1", "status": "playing", "hours_played": 1}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_api_health_check(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_ex1_post_invalid_game_id_type(self):
        data = {"external_game_id": 12345, "status": "playing", "hours_played": 1}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_ex1_post_invalid_game_id_empty(self):
        data = {"external_game_id": "  ", "status": "playing", "hours_played": 1}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_ex4_list_correct_fields(self):
        LibraryEntry.objects.create(user=self.user, external_game_id="f1", status="wishlist", hours_played=0)
        response = self.client.get(self.list_create_url)
        item = response.json()[0]
        self.assertIn("id", item)
        self.assertIn("external_game_id", item)
        self.assertIn("status", item)
        self.assertIn("hours_played", item)

    def test_ex4_detail_correct_fields(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="f1", status="wishlist", hours_played=0)
        detail_url = reverse('entry-detail-update', args=[e.id])
        response = self.client.get(detail_url)
        item = response.json()
        self.assertIn("id", item)
        self.assertIn("external_game_id", item)
        self.assertIn("status", item)
        self.assertIn("hours_played", item)

    # Actualización (PATCH) y Casos Borde (Ejercicio 5)
    def test_ex5_patch_unauthorized(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="patch_unauth", status="wishlist", hours_played=0)
        self.client.logout()
        detail_url = reverse('entry-detail-update', args=[e.id])
        response = self.client.patch(detail_url, data=json.dumps({"status": "playing"}), content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_ex5_patch_only_status(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="patch_status", status="wishlist", hours_played=0)
        detail_url = reverse('entry-detail-update', args=[e.id])
        response = self.client.patch(detail_url, data=json.dumps({"status": "playing"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        e.refresh_from_db()
        self.assertEqual(e.status, "playing")
        self.assertEqual(e.hours_played, 0)

    def test_ex5_patch_only_hours(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="patch_hours", status="wishlist", hours_played=0)
        detail_url = reverse('entry-detail-update', args=[e.id])
        response = self.client.patch(detail_url, data=json.dumps({"hours_played": 10}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        e.refresh_from_db()
        self.assertEqual(e.hours_played, 10)
        self.assertEqual(e.status, "wishlist")

    def test_ex5_patch_invalid_extra_field(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="patch_extra", status="wishlist", hours_played=0)
        detail_url = reverse('entry-detail-update', args=[e.id])
        # Intentar parchear external_game_id (no permitido)
        response = self.client.patch(detail_url, data=json.dumps({"external_game_id": "new_id"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_ex5_patch_invalid_status_type(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="patch_status_type", status="wishlist", hours_played=0)
        detail_url = reverse('entry-detail-update', args=[e.id])
        response = self.client.patch(detail_url, data=json.dumps({"status": 123}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_ex5_patch_invalid_hours_type(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="patch_hours_type", status="wishlist", hours_played=0)
        detail_url = reverse('entry-detail-update', args=[e.id])
        response = self.client.patch(detail_url, data=json.dumps({"hours_played": "ten"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_ex5_patch_boundary_hours_zero(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="patch_zero", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e.id])
        response = self.client.patch(detail_url, data=json.dumps({"hours_played": 0}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        e.refresh_from_db()
        self.assertEqual(e.hours_played, 0)

    def test_ex5_patch_large_hours(self):
        e = LibraryEntry.objects.create(user=self.user, external_game_id="patch_large", status="playing", hours_played=0)
        detail_url = reverse('entry-detail-update', args=[e.id])
        response = self.client.patch(detail_url, data=json.dumps({"hours_played": 999999}), content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_ex1_post_boundary_hours_zero(self):
        data = {"external_game_id": "game_zero", "status": "wishlist", "hours_played": 0}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_ex1_post_long_external_id(self):
        long_id = "a" * 100
        data = {"external_game_id": long_id, "status": "wishlist", "hours_played": 0}
        response = self.client.post(self.list_create_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_ex4_list_user_isolation_strict(self):
        # Crear 10 juegos para el usuario actual y 10 para otro
        for i in range(10):
            LibraryEntry.objects.create(user=self.user, external_game_id=f"userA_{i}", status="wishlist", hours_played=0)
        
        other_user = User.objects.create_user(username="isolation_test", password="password123")
        for i in range(10):
            LibraryEntry.objects.create(user=other_user, external_game_id=f"userB_{i}", status="wishlist", hours_played=0)
            
        response = self.client.get(self.list_create_url)
        # Debería ver los 10 iniciales de userA + los 10 nuevos de userA? 
        # Espera, self.user ya tenía algunos de los tests anteriores (pero cada test es independiente en DB)
        # En Cada test, la DB se limpia. Así que solo debería haber 10.
        self.assertEqual(len(response.json()), 10)
        for item in response.json():
            self.assertTrue(item["external_game_id"].startswith("userA_"))
