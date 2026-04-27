import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from library.utils import validation_error
from .utils import search_games, resolve_games

@require_GET
def catalog_search(request):
    """
    Ruta: GET /api/catalog/search/
    Parámetros: q (string, obligatorio y no vacío)
    """
    query = request.GET.get("q", "").strip()
    
    if not query:
        return validation_error({"q": "El parámetro de búsqueda 'q' es obligatorio y no puede estar vacío."})

    results, error_response = search_games(query)
    
    if error_response:
        return error_response
        
    return JsonResponse(results, safe=False, status=200)

@csrf_exempt
@require_POST
def catalog_resolve(request):
    """
    Ruta: POST /api/catalog/resolve/
    Body JSON: {"external_game_ids": ["1", "2"]}
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return validation_error({"body": "El cuerpo de la petición debe ser JSON válido."})

    ids = body.get("external_game_ids")
    
    if not isinstance(ids, list) or not ids:
        return validation_error({"external_game_ids": "Debe ser una lista de strings no vacía."})
    
    # Nos aseguramos que todos los elementos sean strings
    if not all(isinstance(id, str) for id in ids):
         return validation_error({"external_game_ids": "Todos los IDs deben ser de tipo string."})

    results, error_response = resolve_games(ids)
    
    if error_response:
        return error_response
        
    return JsonResponse(results, safe=False, status=200)
