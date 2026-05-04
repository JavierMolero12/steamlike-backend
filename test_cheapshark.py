
import os
import sys

# Añadimos el directorio actual al path para poder importar el catálogo
sys.path.append(os.getcwd())

# Configuramos Django mínimamente para poder importar utils
import django
from django.conf import settings
if not settings.configured:
    settings.configure()

from catalog.utils import search_games, resolve_games

def test_search():
    print("--- 1. Probando búsqueda para 'Mario' ---")
    results, error = search_games("mario")
    if error:
        print(f"Error: {error}")
        return
    print(f"Encontrados: {len(results)}\n")
    return [r['external_game_id'] for r in results[:2]]

def test_resolve(ids):
    print(f"--- 2. Probando resolución de IDs: {ids} ---")
    results, error = resolve_games(ids)
    if error:
        print(f"Error: {error}")
        return
    for game in results:
        print(f"ID: {game['external_game_id']} -> Título: {game['title']}")

if __name__ == "__main__":
    ids = test_search()
    if ids:
        test_resolve(ids)
