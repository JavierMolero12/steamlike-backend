# steamlike_backend

Backend Django para el proyecto Steamlike (DWES de 2º DAW). Incluye integración con PostgreSQL, Redis para caching y servicios de catálogo externo.

## Integración Continua (CI)
[![Django CI](https://github.com/JavierMolero12/steamlike-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/JavierMolero12/steamlike-backend/actions/workflows/ci.yml)

---

## Guía de Instalación y Arranque

Si acabas de descargar el proyecto, sigue estos pasos para ponerlo en marcha:

### 1) Configuración de variables de entorno
Crea un archivo `.env` en la raíz del proyecto basándote en el ejemplo:
```bash
cp .env.example .env
```
*(Asegúrate de ajustar las credenciales si es necesario).*

### 2) Levantar la infraestructura con Docker
Este comando descargará las imágenes (PostgreSQL, Redis) y construirá el contenedor de la aplicación:
```bash
docker compose up --build -d
```

### 3) Preparar la Base de Datos
Ejecuta las migraciones para crear las tablas necesarias:
```bash
docker compose exec web python manage.py migrate
```

### 4) Crear Superusuario (Acceso al Panel de Control)
```bash
docker compose exec web python manage.py createsuperuser
```

### 5) Verificar Servicios (Caché Redis)
Para comprobar que la conexión con el servicio Redis es correcta (UA9):
```bash
docker compose exec web python manage.py shell < scratch/verify_redis.py
```

---

## Endpoints Principales

- **Admin:** `http://localhost:8000/admin/`
- **Health-check:** `GET http://localhost:8000/health/`
- **Catálogo (Búsqueda):** `GET /api/catalog/search/?q=texto`
- **Biblioteca:** `/api/library/entries/` (Requiere autenticación)

---

## Comandos Útiles

- **Ver logs en tiempo real:** `docker compose logs -f web`
- **Entrar en la shell del contenedor:** `docker compose exec web bash`
- **Parar los contenedores:** `docker compose down`

---

## Desarrollo
- `core`: Utilidades y salud del sistema.
- `library`: Gestión de la biblioteca personal de juegos.
- `catalog`: Integración con CheapShark API y caché Redis.

---
*DevOps Ejercicio 3: Activación de workflow automática.*