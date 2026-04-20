import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import LibraryEntry

@require_GET
def health(request):
    return JsonResponse({"status": "ok"})

def validation_error(details=None):
    data = {
        "error": "validation_error",
        "message": "Datos de entrada inválidos",
    }
    if details is not None:
        data["details"] = details
    return JsonResponse(data, status=400)

def duplicate_entry_error(external_game_id):
    return JsonResponse({
        "error": "duplicate_entry",
        "message": "El juego ya existe en la biblioteca",
        "details": {"external_game_id": "duplicate"}
    }, status=400)

def not_found_error():
    return JsonResponse({
        "error": "not_found",
        "message": "La entrada solicitada no existe"
    }, status=404)

def unauthorized_error():
    return JsonResponse({
        "error": "unauthorized",
        "message": "No autenticado"
    }, status=401)

def entry_to_dict(entry):
    return {
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played
    }

@csrf_exempt
@require_http_methods(["GET", "POST"])
def entries_list_create(request):
    if not request.user.is_authenticated:
        return unauthorized_error()

    if request.method == "GET":
        entries = LibraryEntry.objects.filter(user=request.user).order_by("id")
        return JsonResponse([entry_to_dict(e) for e in entries], safe=False, status=200)

    elif request.method == "POST":
        if not request.body:
            return validation_error()

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return validation_error()

        if not body or not isinstance(body, dict):
            return validation_error()
            
        required_fields = ["external_game_id", "status", "hours_played"]
        details = {}
        for field in required_fields:
            if field not in body:
                details[field] = "Falta el campo"

        if details:
            return validation_error(details)
            
        external_game_id = body.get("external_game_id")
        status = body.get("status")
        hours_played = body.get("hours_played")
        
        if type(external_game_id) is not str:
            details["external_game_id"] = "Debe ser string"
        elif not external_game_id.strip():
             details["external_game_id"] = "Debe ser string no vacio"
        
        if type(status) is not str or status not in LibraryEntry.ALLOWED_STATUSES:
            details["status"] = "Debe ser string y tener un valor permitido"
            
        if type(hours_played) is not int or hours_played < 0:
            details["hours_played"] = "Debe ser integer y >= 0"

        if details:
            return validation_error(details)

        if LibraryEntry.objects.filter(user=request.user, external_game_id=external_game_id).exists():
            return duplicate_entry_error(external_game_id)
            
        entry = LibraryEntry.objects.create(
            user=request.user,
            external_game_id=external_game_id,
            status=status,
            hours_played=hours_played
        )
        return JsonResponse(entry_to_dict(entry), status=201)

@csrf_exempt
@require_http_methods(["GET", "PATCH"])
def entry_detail_update(request, entry_id):
    if not request.user.is_authenticated:
        return unauthorized_error()

    try:
        entry = LibraryEntry.objects.get(id=entry_id)
    except LibraryEntry.DoesNotExist:
        return not_found_error()

    if entry.user != request.user:
        return not_found_error()

    if request.method == "GET":
        return JsonResponse(entry_to_dict(entry), status=200)

    elif request.method == "PATCH":
        if not request.body:
            return validation_error()

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return validation_error()
            
        if not body or not isinstance(body, dict):
            return validation_error()
            
        allowed_fields = ["status", "hours_played"]
        details = {}
        
        for key in body.keys():
            if key not in allowed_fields:
                details[key] = "Campo no permitido"
        
        if details:
            return validation_error(details)
            
        if "status" in body:
            status = body["status"]
            if type(status) is not str or status not in LibraryEntry.ALLOWED_STATUSES:
                details["status"] = "Debe ser string y tener un valor permitido"
                
        if "hours_played" in body:
            hours_played = body["hours_played"]
            if type(hours_played) is not int or hours_played < 0:
                details["hours_played"] = "Debe ser integer y >= 0"
                
        if details:
            return validation_error(details)
            
        if "status" in body:
            entry.status = body["status"]
        if "hours_played" in body:
            entry.hours_played = body["hours_played"]
            
        entry.save()
        return JsonResponse(entry_to_dict(entry), status=200)
