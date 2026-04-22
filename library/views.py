import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import LibraryEntry
from .utils import (
    validation_error, unauthorized_error, duplicate_entry_error, not_found_error, parse_json_body, entry_to_dict
)

# library/views.py - Gestión de la Biblioteca de Juegos

@require_GET
def health(request):
    """Verifica si el servidor está funcionando correctamente"""
    return JsonResponse({"status": "ok"}, status=200)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def entries_list_create(request):
    """
    Ruta: /api/library/entries/
    - GET: Lista todos los juegos del usuario actual.
    - POST: Crea un nuevo juego asociado al usuario actual.
    """
    # Verificamos si el usuario ha iniciado sesión
    if not request.user.is_authenticated:
        return unauthorized_error()

    # --- LISTADO (GET) ---
    if request.method == "GET":
        # Filtramos para que solo vea SUS juegos (Privacidad)
        entries = LibraryEntry.objects.filter(user=request.user)
        return JsonResponse([entry_to_dict(e) for e in entries], safe=False, status=200)

    # --- CREACIÓN (POST) ---
    elif request.method == "POST":
        # Parseamos el JSON recibido
        body, error_response = parse_json_body(request)
        if error_response: return error_response

        # Validaciones de campos obligatorios
        required = ["title", "platform", "external_game_id"]
        details = {}
        for field in required:
            if field not in body or not str(body.get(field)).strip():
                details[field] = "Falta el campo"
        
        if details: return validation_error(details)

        # Evitamos juegos duplicados por su ID externo
        if LibraryEntry.objects.filter(user=request.user, external_game_id=body["external_game_id"]).exists():
            return duplicate_entry_error()

        # Creamos el registro asociándolo al usuario logueado
        entry = LibraryEntry.objects.create(
            user=request.user,
            title=body["title"],
            platform=body["platform"],
            external_game_id=body["external_game_id"],
            status=body.get("status", "wishlist"),
            hours_played=body.get("hours_played", 0)
        )
        return JsonResponse(entry_to_dict(entry), status=201)

@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def entry_detail_update(request, entry_id):
    """
    Ruta: /api/library/entries/{id}/
    Gestiona un juego específico.
    """
    if not request.user.is_authenticated:
        return unauthorized_error()

    # Buscamos el juego. Importante: solo buscamos entre los del usuario actual.
    try:
        entry = LibraryEntry.objects.get(id=entry_id, user=request.user)
    except LibraryEntry.DoesNotExist:
        return not_found_error()

    # --- VER DETALLE (GET) ---
    if request.method == "GET":
        return JsonResponse(entry_to_dict(entry), status=200)

    # --- BORRAR (DELETE) ---
    elif request.method == "DELETE":
        entry.delete()
        return JsonResponse({"ok": True}, status=200)

    # --- SUSTITUCIÓN TOTAL (PUT) - Ejercicio 4 ---
    elif request.method == "PUT":
        body, error_response = parse_json_body(request)
        if error_response: return error_response

        # PUT requiere enviar TODOS los campos para reemplazar el objeto
        required = ["title", "platform", "external_game_id", "status", "hours_played"]
        details = {}
        for field in required:
            if field not in body:
                details[field] = "Este campo es obligatorio en PUT"
        
        if details: return validation_error(details)

        # Actualizamos todos los campos
        entry.title = body["title"]
        entry.platform = body["platform"]
        entry.external_game_id = body["external_game_id"]
        entry.status = body["status"]
        entry.hours_played = body["hours_played"]
        entry.save()
        
        return JsonResponse(entry_to_dict(entry), status=200)

    # --- ACTUALIZACIÓN PARCIAL (PATCH) - Ejercicio 5 ---
    elif request.method == "PATCH":
        body, error_response = parse_json_body(request)
        if error_response: return error_response
        
        if not body:
            return validation_error({"body": "No se han proporcionado campos"})
        
        # Solo permitimos editar estos dos campos según el ejercicio
        allowed_fields = ["status", "hours_played"]
        extra_fields = [f for f in body.keys() if f not in allowed_fields]
        if extra_fields:
            return validation_error({f: "Campo no permitido" for f in extra_fields})

        # Aplicamos los cambios si el dato es válido
        for field in allowed_fields:
            if field in body:
                val = body[field]
                # Validamos tipo de dato y valores permitidos
                if field == "hours_played" and (type(val) is not int or val < 0):
                    return validation_error({field: "Invalido"})
                if field == "status" and val not in ["wishlist", "playing", "completed", "dropped"]:
                    return validation_error({field: "Estado invalido"})
                setattr(entry, field, val)
        
        entry.save()
        return JsonResponse(entry_to_dict(entry), status=200)
