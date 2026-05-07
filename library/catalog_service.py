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
        query_norm = query.lower().strip().replace(' ', '_')
        cache_key = f"catalog_search_{query_norm}"
        
        # 1. Consulta a Redis (Ejercicio 5)
        logger.info(f"Consulta a Redis | Acción: Buscar '{query}'")
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                # Uso de datos cacheados (Ejercicio 5)
                logger.info(f"Uso de datos cacheados | Origen: Redis | Búsqueda: '{query}'")
                return cached_data, None
        except Exception as e:
            logger.warning(f"Fallo de conexión con Redis (get): {e}")
            cached_data = None

        # 2. Consulta al proveedor externo (Ejercicio 5)
        logger.info(f"Consulta al proveedor externo | Acción: CheapShark Search '{query}'")
        url = f"https://www.cheapshark.com/api/1.0/games?title={urllib.parse.quote(query)}"
        
        try:
            data, error_response = CatalogService._fetch_cheapshark(url)
            
            if error_response:
                # Si falla el proveedor, intentamos ver si hay algo en caché (Ejercicio 4)
                # Aunque ya lo miramos arriba, si por algún motivo se pobló o usamos un fallback manual
                logger.error(f"Fallo del proveedor externo. Intentando recuperación...")
                return None, error_response

            # Mapear al formato interno
            results = []
            for item in data:
                game_data = {
                    "external_game_id": str(item.get("gameID", "")),
                    "title": item.get("external", ""),
                    "thumb": item.get("thumb", "")
                }
                results.append(game_data)
                # Opcional: Cachear también el juego individual para check_game_exists
                try:
                    cache.set(f"game_{game_data['external_game_id']}", game_data, timeout=CatalogService.CACHE_TTL)
                except Exception:
                    pass

            # 3. Guardado en Redis (Ejercicio 2)
            try:
                cache.set(cache_key, results, timeout=CatalogService.CACHE_TTL)
                logger.info(f"Acción: Datos guardados en Redis | Búsqueda: '{query}'")
            except Exception as e:
                logger.warning(f"Fallo de conexión con Redis (set): {e}")
            
            return results, None

        except Exception as e:
            logger.error(f"Fallo crítico: {str(e)}")
            return None, CatalogService.error_502()

    @staticmethod
    def resolve_games(ids: list):
        results = []
        missing_ids = []

        # Intentar obtener de caché cada ID
        for game_id in ids:
            try:
                cached = cache.get(f"game_{game_id}")
            except Exception:
                cached = None
                
            if cached:
                results.append(cached)
            else:
                missing_ids.append(game_id)

        if not missing_ids:
            logger.info(f"Uso de datos cacheados | Origen: Redis | Acción: Resolve IDs")
            return results, None

        # Consultar los faltantes
        ids_str = ",".join([str(id) for id in missing_ids])
        url = f"https://www.cheapshark.com/api/1.0/games?ids={urllib.parse.quote(ids_str)}"
        
        logger.info(f"Consulta al proveedor externo | Acción: CheapShark Resolve IDs")
        data, error_response = CatalogService._fetch_cheapshark(url)
        
        if error_response:
            # Si falla y tenemos algunos resultados de caché, podríamos devolverlos, 
            # pero el ejercicio pide gestionar el fallo de forma controlada.
            if results:
                logger.warning(f"Uso de Redis por fallo del proveedor | Datos parciales recuperados")
                return results, None
            return None, error_response
            
        if isinstance(data, dict):
            for game_id, info in data.items():
                game_data = {
                    "external_game_id": str(game_id),
                    "title": info.get("info", {}).get("title", ""),
                    "thumb": info.get("info", {}).get("thumb", "")
                }
                results.append(game_data)
                try:
                    cache.set(f"game_{game_id}", game_data, timeout=CatalogService.CACHE_TTL)
                except Exception:
                    pass

        return results, None

    @staticmethod
    def check_game_exists(game_id: str):
        cache_key = f"game_{game_id}"
        
        # 1. Consulta a Redis
        logger.info(f"Consulta a Redis | Acción: Validar juego {game_id}")
        try:
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"Uso de datos cacheados | Origen: Redis | Juego: {game_id}")
                return True, None
        except Exception:
            cached = None

        # 2. Consulta al proveedor
        logger.info(f"Consulta al proveedor externo | Acción: CheapShark Check {game_id}")
        url = f"https://www.cheapshark.com/api/1.0/games?id={urllib.parse.quote(str(game_id))}"
        
        data, error_response = CatalogService._fetch_cheapshark(url)
        
        if error_response:
            # Re-comprobar caché por si acaso hubo una actualización paralela o queremos ser resilientes
            # Ejercicio 4: "si hay datos en Redis -> usarlos"
            try:
                cached_retry = cache.get(cache_key)
            except Exception:
                cached_retry = None
                
            if cached_retry:
                logger.info(f"Uso de Redis por fallo del proveedor | Recuperado juego {game_id}")
                return True, None
            return False, error_response
        
        if not data or not isinstance(data, dict) or "info" not in data:
            return False, None
            
        # Cachear para futuras validaciones
        game_data = {
            "external_game_id": str(game_id),
            "title": data.get("info", {}).get("title", ""),
            "thumb": data.get("info", {}).get("thumb", "")
        }
        try:
            cache.set(cache_key, game_data, timeout=CatalogService.CACHE_TTL)
        except Exception:
            pass
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
