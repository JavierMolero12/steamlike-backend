# Desarrollo Web en Entorno Servidor - Ejercicios evaluables UA7
**Autor:** Javier Molero

- **URL del Repositorio:** [https://github.com/JavierMolero12/steamlike-backend](https://github.com/JavierMolero12/steamlike-backend)
- **URL del Despliegue:** [https://steamlike-backend-hok7.onrender.com](https://steamlike-backend-hok7.onrender.com)

## Ejercicio 1: Análisis del catálogo y la API CheapShark

Tras analizar la documentación pública de la API de CheapShark (https://apidocs.cheapshark.com/), expongo a continuación las respuestas a las cuestiones planteadas en el ejercicio.

### 1. Endpoints de búsqueda y consulta
*   **Buscar juegos por texto:**
    El endpoint que permite buscar juegos por su título es `GET /api/1.0/games`. Se debe proporcionar el parámetro de consulta `title`.
    *Ejemplo:* `GET https://www.cheapshark.com/api/1.0/games?title=batman`

*   **Consultar información de varios juegos por ID:**
    El mismo endpoint `GET /api/1.0/games` permite la consulta múltiple de juegos si se le pasa el parámetro de consulta `ids`, que acepta una lista de identificadores separados por comas.
    *Ejemplo:* `GET https://www.cheapshark.com/api/1.0/games?ids=128,129,130`

### 2. Autenticación y aspectos relevantes
*   La API de CheapShark **no requiere autenticación** (no es necesario proveer una API key ni tokens) para usar estos endpoints básicos.
*   **Aspectos relevantes a tener en cuenta:**
    *   **User-Agent:** La documentación indica que es una buena práctica y, a menudo, requerido, enviar un encabezado `User-Agent` que identifique la aplicación (por ejemplo, con un correo electrónico) para evitar bloqueos por parte del servidor.
    *   **Rate Limiting (Limitación de tasa):** Aunque no requiere autenticación, el servicio tiene límites de peticiones. Si se excede el volumen razonable de peticiones, la API devolverá un error `429 Too Many Requests`. Por esto es importante controlar la cantidad de llamadas.
    *   **Uso adecuado:** Se especifica que la API debe usarse para responder a peticiones directas de usuarios y no para raspar (scrape) ni hacer volcados completos de la base de datos de CheapShark.

### 3. Decisiones de diseño en nuestro sistema
*   **A `external_game_id` se le asignará el valor del `gameID` de CheapShark.**
    *Por qué:* Al asociar un ID externo único a cada registro de la biblioteca, logramos establecer una relación inequívoca entre el juego de nuestra base de datos local (que apenas almacena el estado y las horas jugadas) y su correspondiente "ficha" en el servicio externo. Si necesitamos información extra de ese juego, el ID nos permite obtenerla de CheapShark rápidamente.

*   **Por qué al frontend solo se le devuelve información mínima del juego (título, miniatura e ID).**
    *Por qué:* Las respuestas de CheapShark pueden ser muy verbosas e incluir mucha información no relevante para el propósito actual del frontend (como ofertas, precios, tiendas, etc.). Retornar únicamente los datos necesarios (ID, título y miniatura) asegura un JSON estable, reduce la cantidad de datos transmitidos por la red mejorando la eficiencia y abstrae al frontend de cambios no relacionados en la estructura de CheapShark.

*   **Por qué el catálogo no se almacena en la base de datos del sistema.**
    *Por qué:* Mantener un catálogo externo sincronizado requeriría un esfuerzo gigantesco de almacenamiento y actualización constante. Al delegar esta responsabilidad a una API externa (CheapShark), nuestro sistema se mantiene ligero y siempre accede a la información más reciente sobre los juegos (nombres y miniaturas) bajo demanda (On-Demand), limitando nuestra base de datos solo a los datos estrictamente de negocio (qué juegos tiene cada usuario, en qué estado y cuántas horas ha jugado).

## Ejercicio 2: Búsqueda en el catálogo
Se ha implementado el endpoint `GET /api/catalog/search/?q={query}` que consulta CheapShark y devuelve los campos acordados.

**Pruebas realizadas:**
*   **Búsqueda válida:** `GET /api/catalog/search/?q=mario` devuelve un código 200 y la lista de juegos.
*   **Validación de parámetro vacío:** `GET /api/catalog/search/?q=` devuelve un código 400 con el error `validation_error`.

## Ejercicio 3: Resolución de IDs
Se ha implementado el endpoint `POST /api/catalog/resolve/` para obtener información de múltiples juegos a la vez sin persistirlos en la base de datos.

**Pruebas realizadas:**
*   **Resolución válida:** Envío de una lista de IDs devuelve la información de título y miniatura de cada uno (Código 200).
*   **Validación de lista vacía:** Envío de `{"external_game_ids": []}` devuelve un código 400 con `validation_error`.

## Ejercicio 4: Manejo de errores externos
Se han contemplado los escenarios de fallo del servicio externo:
*   **Caso A (503):** Simulación de timeout o servicio no disponible.
*   **Caso B (502):** Error en la respuesta del proveedor externo.
*   **Caso C (400):** Intento de añadir un juego con un ID que no existe en CheapShark.

## Ejercicio 5: Flujo completo y validación
Se ha verificado el flujo real:
1. Buscar un juego en el catálogo.
2. Añadirlo a la biblioteca (validando su existencia externa).
3. Listar la biblioteca.
4. Resolver la información visual (título y foto) para el frontend.

---
**Nota para la defensa:** El sistema está diseñado para ser resiliente. Si CheapShark falla, el usuario recibe un mensaje claro indicando que el servicio externo no está disponible, en lugar de un error genérico del servidor.
