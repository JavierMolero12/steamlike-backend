# Ejercicios evaluables UA3 - DevOps en la Práctica
**Alumno:** Javier Molero

## Ejercicio 7: Análisis de Cobertura de Código (Python/Django)

Tras implementar la extensa batería de tests unitarios y de integración para asegurar la funcionalidad y la seguridad de nuestra API (autenticación, privacidad y operaciones CRUD de la biblioteca), se ha procedido a analizar la cobertura de código empleando la herramienta `coverage`.

A continuación se detalla el análisis de los resultados obtenidos tras ejecutar `coverage run manage.py test` y `coverage report -m`.

### 1. Porcentaje Global de Cobertura
El porcentaje global de cobertura obtenido sobre todo el backend en Python es del **90%**, con un total de 93 tests ejecutados de forma exitosa. 
En particular, la aplicación principal de nuestro enfoque en estas semanas (`library`) cuenta con una cobertura prácticamente completa: `library/auth_views.py` (98%), `library/models.py` (97%), y `library/views.py` (93%).

### 2. Módulos y Archivos con Menor Cobertura
Al analizar el desglose, los archivos con la menor cobertura se concentran de forma aislada en la nueva aplicación `catalog` (que sirve de integración con la API externa de CheapShark):

- `catalog/utils.py` con un **19%** de cobertura.
- `catalog/views.py` con un **35%** de cobertura.

*Nota: La baja cobertura en `catalog` se debe a que las pruebas que hemos desarrollado en esta semana de DevOps se centraban en los objetivos de Autenticación y Biblioteca (`library`). De hecho, en los tests de `library` se ha realizado un "mock" del servicio externo para no penalizar la velocidad de los tests ni depender de la red.*

### 3. Identificación de Partes No Cubiertas
Las líneas no cubiertas en los módulos afectados corresponden a la lógica de consumo de la API externa (CheapShark) y su serialización:

- **En `catalog/utils.py` (Líneas 9, 15, 21, 33-51, 59-74, 83-103, 110-118):**
  - No se están ejecutando las peticiones HTTP reales a la API externa (`urllib.request.urlopen`).
  - Falta cubrir el tratamiento de las posibles excepciones de red (Timeout, HTTPError para 404, 502, 503).
  - Tampoco se está cubriendo el parseo de la respuesta JSON para extraer atributos como el nombre (`title`), imagen (`thumb`) o la resolución por IDs múltiples (`check_game_exists`).

- **En `catalog/views.py` (Líneas 14-24, 33-52):**
  - Faltan por ejecutar los endpoints `GET /api/catalog/search/` y `POST /api/catalog/resolve/`.
  - No se cubren las validaciones de las peticiones (como asegurar que se recibe un parámetro de búsqueda `q` válido o un cuerpo JSON adecuado para resolver IDs múltiples).

- **En `library/views.py` y `library/auth_views.py` (Resto de % marginal):**
  - El 2-7% restante en estos ficheros corresponde típicamente a casos de error muy aislados o de formato inválido de JSON (`json.JSONDecodeError`) que resultan difíciles de forzar directamente o que están cubiertos por un decorador intermedio, así como líneas defensivas para atrapar excepciones genéricas no previstas (por ejemplo bloques `except Exception:`).

### 4. Propuesta de Priorización y Mejora de Cobertura

Para alcanzar un porcentaje de cobertura superior (cercano al 98-100%) priorizando la calidad del software, propongo la siguiente estrategia:

1. **Prioridad Alta: Tests Unitarios con Mocks para `catalog/utils.py`**
   - **Qué hacer:** Crear una suite de pruebas específica (`catalog/tests.py`) que verifique la lógica de `catalog/utils.py`.
   - **Tipo de test:** Tests unitarios utilizando la librería `unittest.mock` (especialmente `@patch('urllib.request.urlopen')`).
   - **Justificación:** Se deben probar todos los flujos de error que hemos definido en el código (simular un *timeout*, devolver un *Error 502 Bad Gateway*, simular un *404 Not Found* de CheapShark). Al ser un servicio externo, **no debemos** hacer peticiones reales en los tests para evitar latencia e inestabilidad; simular la respuesta nos dará el control para cubrir todas esas líneas de manejo de errores de forma robusta.

2. **Prioridad Media: Tests de Integración para `catalog/views.py`**
   - **Qué hacer:** Simular peticiones `GET` y `POST` a los endpoints del catálogo utilizando el `Client` de pruebas de Django.
   - **Tipo de test:** Tests de integración (aislando la base de datos y la red externa).
   - **Justificación:** Hay que asegurar que la vista serializa correctamente los datos recibidos por el `utils` o devuelve códigos `400 Bad Request` si al llamar a `GET /api/catalog/search/` no se incluye el parámetro `q` de búsqueda. Estos tests son idénticos a los que ya hemos hecho para `library` y aumentarán drásticamente el 35% actual.

3. **Prioridad Baja: Tests de Robustez en Deserialización JSON**
   - **Qué hacer:** Probar a enviar cuerpos (bodies) completamente corruptos y mal formados a nivel de bytes en aquellos lugares de `library` que se nos escapan.
   - **Justificación:** Esto permitirá recorrer los últimos bloques `except json.JSONDecodeError:` logrando un código backend a prueba de fallos críticos, logrando el 100% de cobertura en la lógica crítica.
