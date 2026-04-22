# Respuestas Teóricas UA7 - DevOps y Backend

## Ejercicio 1: Métodos HTTP y Códigos de Estado

### Métodos HTTP utilizados en Steamlike
En este proyecto hemos aplicado los verbos HTTP siguiendo los principios REST:

1.  **GET**: Se utiliza para **recuperar** información. 
    *   *Ejemplo*: `GET /api/library/entries/` para listar mis juegos o `GET /api/users/me/` para ver mi perfil. No modifica el estado del servidor.
2.  **POST**: Se utiliza para **crear** nuevos recursos o realizar acciones que no son idempotentes.
    *   *Ejemplo*: `POST /api/library/entries/` para añadir un juego nuevo o `POST /api/auth/login/` para iniciar una sesión.
3.  **PUT**: Se utiliza para la **sustitución completa** de un recurso. Requiere enviar todos los campos.
    *   *Ejemplo*: `PUT /api/library/entries/{id}/`. Si el juego tenía 10 horas y estado "playing", y mandamos un PUT con 0 horas y "wishlist", el recurso se sobreescribe totalmente.
4.  **PATCH**: Se utiliza para la **actualización parcial** de un recurso. Solo enviamos los campos que queremos cambiar.
    *   *Ejemplo*: `PATCH /api/library/entries/{id}/` para cambiar solo las horas jugadas sin tocar el título o el estado.
5.  **DELETE**: Se utiliza para **eliminar** un recurso.
    *   *Ejemplo*: `DELETE /api/users/me/` para borrar mi cuenta o `DELETE /api/library/entries/{id}/` para quitar un juego de mi lista.

### Códigos de Estado (Status Codes)
Hemos implementado los siguientes códigos para dar feedback preciso al cliente:

*   **200 OK**: La petición ha tenido éxito. (Ej: Listado de juegos).
*   **201 Created**: Recurso creado con éxito. (Ej: Registro de usuario o creación de entrada).
*   **240 No Content**: Petición éxito pero sin cuerpo de respuesta. (Ej: Logout o Borrado de cuenta).
*   **400 Bad Request**: Error del cliente (JSON malformado, faltan campos, tipos incorrectos). Devuelve `validation_error`.
*   **401 Unauthorized**: El usuario no está autenticado o sus credenciales son inválidas.
*   **403 Forbidden**: El usuario está autenticado pero no tiene permisos para esa acción (aunque en este proyecto usamos a menudo 404 para no revelar la existencia de recursos ajenos).
*   **404 Not Found**: El recurso solicitado no existe o no pertenece al usuario.
*   **409 Conflict**: (No usado explícitamente pero común para duplicados, aunque nosotros usamos 400 con `duplicate_entry`).
*   **500 Internal Server Error**: Error inesperado en el servidor (ej: fallo de base de datos).

---

## Ejercicio 5: Análisis del endpoint PATCH

### Valoración del endpoint `PATCH /api/library/entries/{id}/`

1.  **Idoneidad del método**: PATCH es el método más adecuado para este endpoint porque en una biblioteca de juegos es muy común querer actualizar **solo un dato** (ej: sumar horas después de jugar) sin tener que enviar de nuevo el ID externo del juego que no va a cambiar.
2.  **Comprobación de usuario**: Es **crítico** comprobar que el dueño del recurso sea el mismo que hace la petición (`entry.user == request.user`). Sin esta comprobación, cualquier usuario autenticado podría modificar las horas de juego de otros usuarios solo conociendo el ID numérico, lo cual sería un fallo de seguridad grave (Broken Object Level Authorization).
3.  **Códigos de estado**:
    *   **200**: Correcto para una actualización exitosa.
    *   **400**: Necesario si el usuario intenta mandar campos que no existen o valores inválidos (ej: horas negativas).
    *   **401**: Imprescindible para proteger la privacidad.
    *   **404**: Se devuelve 404 cuando la entrada no existe **o no es del usuario**, lo cual es una buena práctica de seguridad para evitar que atacantes adivinen IDs de otros usuarios (ofuscación).
4.  **Comportamiento coherente**: El endpoint es coherente con el resto de la API al usar el formato de error JSON `{"error": "...", "message": "..."}`.
