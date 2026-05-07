import os
import sys
import django
from django.core.cache import cache

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steamlike_backend.settings')
django.setup()

def verify_redis():
    print("--- Verificación de Conexión a Redis (UA9 - Ejercicio 1) ---")
    
    try:
        # 1. Intentar escribir un valor
        print("Intentando escribir en Redis...")
        cache.set("test_connection", "Redis está funcionando correctamente", timeout=30)
        
        # 2. Intentar leer el valor
        print("Intentando leer de Redis...")
        value = cache.get("test_connection")
        
        if value == "Redis está funcionando correctamente":
            print("\033[92m¡ÉXITO! Django se ha conectado a Redis correctamente.\033[0m")
            print(f"Valor recuperado: {value}")
        else:
            print("\033[91mFALLO: El valor recuperado no coincide.\033[0m")
            
    except Exception as e:
        print("\033[91mERROR: No se ha podido conectar con Redis.\033[0m")
        print(f"Detalles: {str(e)}")
        print("\nConsejo: Asegúrate de que los contenedores de Docker estén levantados (docker-compose up)")

if __name__ == "__main__":
    verify_redis()
