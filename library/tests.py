import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import LibraryEntry

class LibraryAPIExcercisesTests(TestCase):
    def setUp(self):
        self.client = Client()
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
        e1 = LibraryEntry.objects.create(external_game_id="g1", status="wishlist", hours_played=0)
        e2 = LibraryEntry.objects.create(external_game_id="g2", status="playing", hours_played=20)
        
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
        e1 = LibraryEntry.objects.create(external_game_id="game_patch", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        
        data = {"status": "completed", "hours_played": 50}
        response = self.client.patch(detail_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data["status"], "completed")
        self.assertEqual(resp_data["hours_played"], 50)
        
    def test_ex5_patch_invalid_empty(self):
        e1 = LibraryEntry.objects.create(external_game_id="game_patch_2", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        response = self.client.patch(detail_url, data=json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        
    def test_ex5_patch_invalid_status(self):
        e1 = LibraryEntry.objects.create(external_game_id="game_patch_3", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        response = self.client.patch(detail_url, data=json.dumps({"status": "invalid_status"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        
    def test_ex5_patch_invalid_hours(self):
        e1 = LibraryEntry.objects.create(external_game_id="game_patch_4", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        response = self.client.patch(detail_url, data=json.dumps({"hours_played": -10}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        
    def test_ex5_patch_unknown_field(self):
        e1 = LibraryEntry.objects.create(external_game_id="game_patch_5", status="playing", hours_played=10)
        detail_url = reverse('entry-detail-update', args=[e1.id])
        response = self.client.patch(detail_url, data=json.dumps({"status": "completed", "extra_field": "hello"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("extra_field", response.json()["details"])
        
    def test_ex5_patch_not_found(self):
        detail_url = reverse('entry-detail-update', args=[9999])
        response = self.client.patch(detail_url, data=json.dumps({"status": "completed"}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
