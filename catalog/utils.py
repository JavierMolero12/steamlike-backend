import json
import urllib.request
import urllib.error
import urllib.parse
from django.http import JsonResponse

# Respuestas predefinidas de error
def external_service_unavailable():
    return JsonResponse({
        "error": "external_service_unavailable",
        "message": "El catálogo externo no está disponible. Inténtalo más tarde."
    }, status=503)

def external_service_error():
    return JsonResponse({
        "error": "external_service_error",
        "message": "Error al consultar el catálogo externo."
    }, status=502)

def invalid_external_game_id():
    return JsonResponse({
        "error": "invalid_external_game_id",
        "message": "El juego indicado no existe en el catálogo externo.",
        "details": {"external_game_id": "not_found"}
    }, status=400)


def _fetch_cheapshark(url: str):
    """
    Función interna para hacer la petición HTTP a CheapShark.
    Retorna (data, error_response, is_404). Si error_response es None, la petición tuvo éxito o fue 404.
    """
    req = urllib.request.Request(url, headers={'User-Agent': 'SteamlikeApp/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                return None, external_service_error(), False
            data = json.loads(response.read().decode())
            return data, None, False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None, True
        return None, external_service_error(), False
    except urllib.error.URLError as e:
        # Timeout o problemas de red
        if isinstance(e.reason, TimeoutError) or "timeout" in str(e.reason).lower():
            return None, external_service_unavailable(), False
        return None, external_service_unavailable(), False
    except Exception:
        # Cualquier otro error en la petición o en el parseo JSON
        return None, external_service_error(), False


def search_games(query: str):
    """
    Busca juegos por título.
    Retorna (lista_juegos, error_response).
    """
    url = f"https://www.cheapshark.com/api/1.0/games?title={urllib.parse.quote(query)}"
    data, error, is_404 = _fetch_cheapshark(url)
    if error:
        return None, error
    if is_404 or not data:
        return [], None
    
    # Mapear a nuestro formato
    results = []
    for item in data:
        results.append({
            "external_game_id": str(item.get("gameID", "")),
            "title": item.get("external", ""),
            "thumb": item.get("thumb", "")
        })
    return results, None


def resolve_games(ids: list):
    """
    Obtiene los detalles de varios juegos por IDs.
    Retorna (lista_juegos, error_response).
    """
    # Validar formato
    if not ids or not isinstance(ids, list):
        return [], None
        
    ids_str = ",".join([str(id) for id in ids])
    url = f"https://www.cheapshark.com/api/1.0/games?ids={urllib.parse.quote(ids_str)}"
    data, error, is_404 = _fetch_cheapshark(url)
    if error:
        return None, error
    if is_404 or not data:
        return [], None

    results = []
    # La respuesta para ids es un diccionario donde las claves son los IDs
    if isinstance(data, dict):
        for game_id, info in data.items():
            results.append({
                "external_game_id": str(game_id),
                "title": info.get("info", {}).get("title", ""),
                "thumb": info.get("info", {}).get("thumb", "")
            })
    return results, None

def check_game_exists(game_id: str):
    """
    Verifica si un juego existe en CheapShark.
    Retorna (existe_bool, error_response).
    """
    url = f"https://www.cheapshark.com/api/1.0/games?id={urllib.parse.quote(str(game_id))}"
    data, error, is_404 = _fetch_cheapshark(url)
    if error:
        return False, error
        
    if is_404 or not data or not isinstance(data, dict) or "info" not in data:
        return False, None
        
    return True, None
