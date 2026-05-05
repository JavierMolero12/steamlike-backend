import logging
import json
import urllib.request
import urllib.error
import urllib.parse
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class CatalogService:
    """
    Servicio centralizado para la gestión del catálogo externo y caché Redis (UA9).
    """
    CACHE_TTL = 300  # 5 minutos de caché

    @staticmethod
    def search_games(query: str):
        cache_key = f"catalog_search_{query.lower().replace(' ', '_')}"
        
        # 1. Intentar obtener de Redis (Ejercicio 2 y 5)
        logger.info(f"Acción: Consulta a Redis | Búsqueda: '{query}'")
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Uso de datos cacheados | Origen: Redis | Resultado: Éxito")
            return cached_data, None

        # 2. Si no está en caché, consultar al proveedor (Ejercicio 2 y 5)
        logger.info(f"Consulta al proveedor externo (CheapShark) | Búsqueda: '{query}'")
        url = f"https://www.cheapshark.com/api/1.0/games?title={urllib.parse.quote(query)}"
        
        try:
            data, error_response = CatalogService._fetch_cheapshark(url)
            
            if error_response:
                # Si falla el proveedor, Exercise 4: "si hay datos en Redis -> usarlos"
                # (En este punto sabemos que cache.get devolvió None, por lo que no hay datos disponibles)
                logger.error(f"Error en el proveedor externo | Búsqueda: '{query}' | Fallo del sistema")
                return None, error_response

            # Mapear al formato interno
            results = []
            for item in data:
                results.append({
                    "external_game_id": str(item.get("gameID", "")),
                    "title": item.get("external", ""),
                    "thumb": item.get("thumb", "")
                })

            # 3. Guardar en Redis para futuras consultas (Ejercicio 2)
            cache.set(cache_key, results, timeout=CatalogService.CACHE_TTL)
            logger.info(f"Acción: Guardado en Redis | Búsqueda: '{query}' | Resultado: Nuevo dato cacheado")
            
            return results, None

        except Exception as e:
            logger.error(f"Fallo crítico al procesar búsqueda externa: {str(e)}")
            return None, CatalogService.error_502()

    @staticmethod
    def resolve_games(ids: list):
        # Para este ejercicio nos centramos en la caché de búsqueda, 
        # pero centralizamos también la resolución de IDs aquí.
        ids_str = ",".join([str(id) for id in ids])
        url = f"https://www.cheapshark.com/api/1.0/games?ids={urllib.parse.quote(ids_str)}"
        
        data, error_response = CatalogService._fetch_cheapshark(url)
        if error_response:
            return None, error_response
            
        results = []
        if isinstance(data, dict):
            for game_id, info in data.items():
                results.append({
                    "external_game_id": str(game_id),
                    "title": info.get("info", {}).get("title", ""),
                    "thumb": info.get("info", {}).get("thumb", "")
                })
        return results, None

    @staticmethod
    def check_game_exists(game_id: str):
        url = f"https://www.cheapshark.com/api/1.0/games?id={urllib.parse.quote(str(game_id))}"
        data, error_response = CatalogService._fetch_cheapshark(url)
        if error_response:
            return False, error_response
        
        if not data or not isinstance(data, dict) or "info" not in data:
            return False, None
        return True, None

    @staticmethod
    def _fetch_cheapshark(url: str):
        req = urllib.request.Request(url, headers={'User-Agent': 'SteamlikeApp/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status != 200:
                    return None, CatalogService.error_502()
                return json.loads(response.read().decode()), None
        except urllib.error.HTTPError:
            return None, CatalogService.error_502()
        except (urllib.error.URLError, TimeoutError):
            return None, CatalogService.error_503()
        except Exception:
            return None, CatalogService.error_502()

    @staticmethod
    def error_503():
        return JsonResponse({
            "error": "external_service_unavailable",
            "message": "El catálogo externo no está disponible. Inténtalo más tarde."
        }, status=503)

    @staticmethod
    def error_502():
        return JsonResponse({
            "error": "external_service_error",
            "message": "Error al consultar el catálogo externo."
        }, status=502)
