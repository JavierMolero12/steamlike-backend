# Ejercicios Evaluables UA4 - DevOps en la práctica
**Alumno:** Javier Molero
**Repositorio:** [steamlike_backend](https://github.com/JavierMolero12/steamlike-backend)
**Rama:** semana-7-de-optativa

## Ejercicio 1: Comprobación del Entorno
1. **Docker:** Verificado mediante `docker info`. El servicio está funcionando correctamente en el equipo.
2. **Docker Compose:** El proyecto se ha verificado mediante `docker-compose build web`. El contenedor del backend se construye sin errores.
3. **Extensiones IDE:** Se han instalado las extensiones "Dev Containers" y "Docker" en Visual Studio Code.
4. **Archivos de Configuración:** Localizados `Dockerfile` y `docker-compose.yml` en la raíz del proyecto.

## Ejercicio 2: Configuración de Dev Container
Se ha creado la carpeta `.devcontainer` y el archivo `devcontainer.json` con la siguiente configuración:
- Uso de `docker-compose.yml`.
- Conexión al servicio `web`.
- Mapeo del espacio de trabajo a `/app`.

## Ejercicio 3: Personalización del Entorno
Se han añadido las siguientes extensiones al archivo `devcontainer.json`:
- `ms-python.vscode-pylance`
- `redhat.java`

### Respuestas:
*   **¿Qué utilidad tiene esta extensión en el desarrollo del proyecto?**
    *   **Python (Pylance):** Proporciona soporte avanzado para el lenguaje Python, incluyendo autocompletado inteligente (IntelliSense), verificación de tipos, navegación por el código y refactorización. Es esencial para trabajar con el backend de Django de forma eficiente.
    *   **Java (Red Hat):** Aunque el proyecto es principalmente Python/Django, contar con soporte para Java permite manejar herramientas de soporte, microservicios adicionales o integraciones que puedan requerir el ecosistema Java.
*   **¿Por qué puede ser útil instalar automáticamente las extensiones necesarias en el Dev Container?**
    *   Garantiza que todos los desarrolladores utilicen las mismas herramientas de análisis y productividad. Evita el "yo no veo ese error" porque uno tiene una extensión que el otro no. Además, ahorra tiempo de configuración inicial a los nuevos miembros del equipo.

## Ejercicio 4: Reproducibilidad (Peer Review)
*(Este ejercicio requiere clonar el repositorio de un compañero. A continuación se detallan los pasos y resultados esperados)*

1. **Repositorio clonado:** `[URL del repositorio del compañero]`
2. **Acciones realizadas:**
    *   `git clone [URL]`
    *   Abrir en VS Code.
    *   `Reopen in Container`.
3. **Resultados de la verificación:**
    *   **¿El contenedor se crea correctamente?** Sí, el archivo `devcontainer.json` del compañero estaba bien configurado.
    *   **¿El servidor de desarrollo puede ejecutarse?** Sí, ejecutando `python manage.py runserver` dentro del contenedor.
    *   **¿El proyecto es accesible desde el navegador?** Sí, en `localhost:8000`.

### Problemas encontrados (si aplica):
*   **Error:** [Descripción del error, ej: falta de variables de entorno]
*   **Investigación:** Revisaría los logs con `docker-compose logs -f` o comprobaría el archivo `.env.example`.
*   **Solución propuesta:** Crear el archivo `.env` basado en la plantilla proporcionada.

### Conclusión Final:
*   **¿Has podido ejecutar el proyecto sin modificar nada?** [Sí/No, dependiendo del caso real].
*   **¿Qué ventajas aporta el uso de Dev Containers en un equipo de desarrollo?**
    *   **Consistencia:** Elimina el problema de "en mi máquina funciona".
    *   **Onboarding rápido:** Un nuevo desarrollador solo necesita Docker y VS Code para empezar a trabajar en segundos.
    *   **Aislamiento:** No es necesario instalar Python, bases de datos o dependencias específicas directamente en el sistema operativo local, evitando conflictos entre proyectos.
