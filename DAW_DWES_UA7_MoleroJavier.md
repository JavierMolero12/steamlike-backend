# Desarrollo Web en Entorno Servidor - Ejercicios evaluables UA7
**Autor:** Javier Molero

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
