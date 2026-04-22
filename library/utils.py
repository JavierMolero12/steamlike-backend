import json
from django.http import JsonResponse

# library/utils.py - Funciones auxiliares para la API

def validation_error(details=None):
    """Devuelve un error 400 cuando los datos enviados no son válidos"""
    data = {
        "error": "validation_error",
        "message": "Datos de entrada inválidos",
    }
    if details is not None:
        data["details"] = details
    return JsonResponse(data, status=400)

def duplicate_entry_error(message="El juego ya existe en la biblioteca"):
    """Error cuando se intenta crear un juego que ya tienes"""
    return JsonResponse({
        "error": "duplicate_entry",
        "message": message,
        "details": {"external_game_id": "duplicate"}
    }, status=400)

def not_found_error(message="La entrada solicitada no existe"):
    """Error 404 cuando buscas un juego o usuario que no existe"""
    return JsonResponse({
        "error": "not_found",
        "message": message
    }, status=404)

def unauthorized_error(message="No autenticado"):
    """Error 401 cuando el usuario no ha hecho login"""
    return JsonResponse({
        "error": "unauthorized",
        "message": message
    }, status=401)

def parse_json_body(request):
    """
    Intenta leer el cuerpo de la petición como JSON.
    Si falla, devuelve un error 400 automáticamente.
    """
    try:
        if not request.body:
            return {}, None
        body = json.loads(request.body)
        if not isinstance(body, dict):
            return None, validation_error()
        return body, None
    except json.JSONDecodeError:
        return None, validation_error()

def entry_to_dict(entry):
    """
    Convierte un objeto LibraryEntry de la base de datos a un diccionario.
    Esto permite que Django lo pueda enviar como JSON fácilmente.
    """
    return {
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played
    }
