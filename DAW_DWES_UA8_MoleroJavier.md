# Desarrollo Web en Entorno Servidor - UA8
**Alumno:** Javier Molero
**Repositorio Github:** [Enlace al repositorio](https://github.com/JavierMolero12/steamlike-backend/tree/semana5_ua8)

## Ejercicio 1: Servicio Email (EmailService)
Se ha creado un módulo interno `steamlike_backend/services/email_service.py` que implementa la clase `EmailService`.
* Este servicio utiliza la API de Maileroo (configurable vía variables de entorno).
* Se capturan los timeouts y problemas de red levantando la excepción `ExternalServiceUnavailable` que internamente es un error HTTP 503.
* Si el servicio externo (Maileroo) responde con un código superior o distinto a 200, se propaga un error `ExternalServiceError` equivalente a un 502.

## Ejercicio 2: Endpoint de Depuración (Debug)
Se ha habilitado la ruta `POST /api/debug/email/test/` dentro del paquete `core/urls.py` con su lógica en `core/views.py`.
* **Seguridad:** Solo es accesible si `DEBUG = True`. En caso contrario devuelve un 404.
* **Manejo de errores controlados:** Si no se validan los parámetros obligatorios (`to`, `subject`, `text`), se devuelve un HTTP 400. Si hay fallos de comunicación con el servicio externo se devuelven 502 o 503 según corresponda al error interno levantado por el servicio de email.

### Evidencias Ejercicio 2:
```text
--- EJERCICIO 2: PRUEBAS DEL ENDPOINT DEBUG ---
1. Petición correcta -> Status: 200, Body: {'ok': True}
2a. Inválida (JSON vacío) -> Status: 400, Body: {'error': 'validation_error', 'fields': {'to': 'Field required', 'subject': 'Field required', 'text': 'Field required'}}
2b. Inválida (Falta 'to') -> Status: 400, Body: {'error': 'validation_error', 'fields': {'to': 'Field required'}}
2c. Inválida ('to' no string) -> Status: 400, Body: {'error': 'validation_error', 'fields': {'to': 'Must be a string'}}
3. Forzar 503 (Timeout) -> Status: 503, Body: {'error': 'external_service_unavailable'}
4. Forzar 502 (Error proveedor) -> Status: 502, Body: {'error': 'external_service_error'}
```

## Ejercicio 3: Registro de Trazas (Logs)
Se ha utilizado el módulo nativo `logging` de Python en `email_service.py` para llevar un control estricto de la actividad de los correos:
* Al intentar un envío, imprime por consola *"Attempting to send email"* junto con la acción, el destino y (si es aplicable) el ID del usuario.
* Al ocurrir un fallo de red o del proveedor de correo (timeout), reporta explícitamente *"Fallo por timeout/red"* o *"Fallo por respuesta del proveedor"*.
* Nunca se imprimen variables de entorno críticas como los API Keys por seguridad en el log.

## Ejercicio 4: Extender Registro con Email
La vista de registro existente en `library/auth_views.py` ahora requiere de un parámetro `email` en la petición.
* Se ha añadido validación de formato básico comprobando la existencia del carácter `@`.
* Si el campo no existe o es inválido, se devuelve un error de validación `400 Bad Request`.
* En la respuesta `201 Created` de éxito, el JSON ahora incluye el campo `email`.

## Ejercicio 5: Reacción Automática al Registro de Usuarios
Dentro de la misma función de registro en `auth_views.py`, tras registrar al usuario se llama a `EmailService.send_email(...)`.
* El proceso está envuelto en un bloque `try ... except EmailServiceError:` para garantizar que un fallo en el servidor de correo o la conexión externa **no aborte la creación de la cuenta en la base de datos**.
* El sistema logra mantener la creación del usuario e imprimir los logs correspondientes en caso de error.

### Evidencias Ejercicio 5:
```text
--- EJERCICIO 5: PRUEBAS DE REGISTRO INTEGRADO ---
1. Registro OK (Email OK) -> Status: 201, Body: {'id': 4, 'username': 'user_ok', 'email': 'user_ok@example.com'}
2. Registro OK (Email Fail 502) -> Status: 201, Body: {'id': 5, 'username': 'user_fail', 'email': 'user_fail@example.com'}
```

*(Nota: Estas evidencias se han generado utilizando el script `test_ua8_evidence.py` incluido en el directorio raíz del proyecto)*
