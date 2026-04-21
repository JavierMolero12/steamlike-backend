import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_registration():
    print("\n--- Testing Registration ---")
    
    # 1. Registro correcto (201)
    payload = {"username": "ana", "password": "password123"}
    r = requests.post(f"{BASE_URL}/auth/register/", json=payload)
    print(f"Correcto (201): {r.status_code}, {r.json()}")
    
    # 2. Registro inválido: Username repetido (400)
    r = requests.post(f"{BASE_URL}/auth/register/", json=payload)
    print(f"Repetido (400): {r.status_code}, {r.json()}")
    
    # 3. Registro inválido: Password corta (400)
    payload_short = {"username": "pepe", "password": "123"}
    r = requests.post(f"{BASE_URL}/auth/register/", json=payload_short)
    print(f"Password corta (400): {r.status_code}, {r.json()}")
    
    # 4. Registro inválido: Campos ausentes (400)
    r = requests.post(f"{BASE_URL}/auth/register/", json={"username": "pepe"})
    print(f"Falta password (400): {r.status_code}, {r.json()}")
    
    # 5. Registro inválido: JSON vacío (400)
    r = requests.post(f"{BASE_URL}/auth/register/", json={})
    print(f"JSON vacío (400): {r.status_code}, {r.json()}")

def test_auth_and_library():
    print("\n--- Testing Login & Library ---")
    session = requests.Session()
    
    # 1. Get /me sin autenticar (401)
    r = requests.get(f"{BASE_URL}/users/me/")
    print(f"Get /me sin auth (401): {r.status_code}, {r.json()}")
    
    # 2. Login incorrecto (401)
    r = session.post(f"{BASE_URL}/auth/login/", json={"username": "ana", "password": "wrong"})
    print(f"Login incorrecto (401): {r.status_code}, {r.json()}")
    
    # 3. Login correcto (200)
    r = session.post(f"{BASE_URL}/auth/login/", json={"username": "ana", "password": "password123"})
    print(f"Login correcto (200): {r.status_code}, {r.json()}")
    
    # 4. Get /me después de login (200)
    r = session.get(f"{BASE_URL}/users/me/")
    print(f"Get /me con auth (200): {r.status_code}, {r.json()}")
    
    # 5. Crear entrada de biblioteca
    entry_payload = {
        "external_game_id": "game1",
        "status": "playing",
        "hours_played": 10
    }
    r = session.post(f"{BASE_URL}/library/entries/", json=entry_payload)
    print(f"Crear entrada (201): {r.status_code}, {r.json()}")
    entry_id = r.json()["id"]
    
    # 6. Listar entradas
    r = session.get(f"{BASE_URL}/library/entries/")
    print(f"Listar entradas (200): {r.status_code}, {r.json()}")
    
    # 7. Acceso a detalle
    r = session.get(f"{BASE_URL}/library/entries/{entry_id}/")
    print(f"Detalle (200): {r.status_code}, {r.json()}")
    
    # 8. Test otro usuario
    session2 = requests.Session()
    session2.post(f"{BASE_URL}/auth/register/", json={"username": "jose", "password": "password123"})
    session2.post(f"{BASE_URL}/auth/login/", json={"username": "jose", "password": "password123"})
    
    # Intentar ver entrada de ana (404 esperado)
    r = session2.get(f"{BASE_URL}/library/entries/{entry_id}/")
    print(f"Acceso a entrada ajena (404): {r.status_code}, {r.json()}")
    
    # Listar (debe estar vacía para jose)
    r = session2.get(f"{BASE_URL}/library/entries/")
    print(f"Listar jose (200, []): {r.status_code}, {r.json()}")

if __name__ == "__main__":
    try:
        test_registration()
        test_auth_and_library()
    except Exception as e:
        print(f"Error durante los tests: {e}")
