from pathlib import Path
import os
import sys
import socket

# BASE_DIR: Define la ruta raíz del proyecto en el ordenador. 
# Se usa para localizar archivos como la base de datos SQLite.
BASE_DIR = Path(__file__).resolve().parent.parent

# Funciones auxiliares para leer variables de entorno (.env)
# Esto es una buena práctica para no escribir contraseñas directamente en el código.
def _env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)

def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}

def _env_csv(name: str, default_csv: str = "") -> list[str]:
    raw = os.environ.get(name, default_csv)
    items = [x.strip() for x in raw.split(",") if x.strip()]
    return items

# --- CONFIGURACIÓN DE SEGURIDAD ---
# SECRET_KEY: Clave única para firmar sesiones y tokens. Imprescindible para la seguridad.
SECRET_KEY = _env("DJANGO_SECRET_KEY", "change-me")

# DEBUG: Si es True, muestra errores detallados (útil en desarrollo). 
# En producción debe ser siempre False por seguridad.
DEBUG = _env_bool("DJANGO_DEBUG", False)

# ALLOWED_HOSTS: Dominios desde los que se puede acceder al servidor (localhost, 127.0.0.1).
ALLOWED_HOSTS = _env_csv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

# --- APLICACIONES (INSTALLED_APPS) ---
# Aquí registramos tanto las apps internas de Django (admin, auth, etc.) 
# como nuestra propia aplicación ('library').
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",  # Para permitir peticiones desde el frontend
    "library",      # Nuestra aplicación de juegos
    "catalog",      # Nuestra aplicación de catálogo de juegos
]

# --- MIDDLEWARE ---
# Son capas que procesan cada petición antes de llegar a la vista.
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", # Gestiona permisos de dominios externos (CORS)
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", # Gestiona las sesiones de usuario
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", # Protección contra ataques CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware", # Asocia usuarios a las peticiones
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ROOT_URLCONF: Indica dónde está el archivo de rutas principal.
ROOT_URLCONF = "steamlike_backend.urls"

# TEMPLATES: Configuración para el motor de plantillas HTML de Django.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "steamlike_backend.wsgi.application"

# --- CONFIGURACIÓN DE BASE DE DATOS ---
# Función para detectar si estamos en Docker (buscando el host 'db')
def _is_db_reachable():
    try:
        socket.gethostbyname(_env("POSTGRES_HOST", "db"))
        return True
    except socket.gaierror:
        return False

# Si estamos haciendo tests o no hay base de datos Postgres (Docker), usamos SQLite local.
if 'test' in sys.argv or not _is_db_reachable():
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Configuración para PostgreSQL (Entorno Docker/Producción)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _env("POSTGRES_DB", "steamlike"),
            "USER": _env("POSTGRES_USER", "steamlike"),
            "PASSWORD": _env("POSTGRES_PASSWORD", "steamlike"),
            "HOST": _env("POSTGRES_HOST", "db"),
            "PORT": _env("POSTGRES_PORT", "5432"),
        }
    }

# VALIDACIÓN DE CONTRASEÑAS: Reglas de seguridad para las claves de usuario.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- INTERNACIONALIZACIÓN ---
LANGUAGE_CODE = "es-es" # Idioma español
TIME_ZONE = "Europe/Madrid" # Zona horaria de España
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS ---
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CONFIGURACIÓN CORS (Crucial para el Frontend) ---
# Indicamos qué dominios pueden hacer peticiones a nuestra API (ej: el puerto 3000 o 5173 del frontend).
CORS_ALLOWED_ORIGINS = _env_csv("DJANGO_CORS_ALLOWED_ORIGINS", "http://frontend:3000,http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173")
# Permite que se envíen las cookies de sesión en las peticiones AJAX.
CORS_ALLOW_CREDENTIALS = _env_bool("DJANGO_CORS_ALLOW_CREDENTIALS", True)

# CSRF: Dominios de confianza para formularios.
CSRF_TRUSTED_ORIGINS = _env_csv("DJANGO_CSRF_TRUSTED_ORIGINS", "http://frontend:3000,http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173")

# Configuración de cookies para facilitar el desarrollo local.
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
