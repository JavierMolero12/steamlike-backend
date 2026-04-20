import json
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

def unauthorized_error(message="No autenticado"):
    return JsonResponse({
        "error": "unauthorized",
        "message": message
    }, status=401)

def validation_error(details=None):
    data = {
        "error": "validation_error",
        "message": "Datos de entrada inválidos",
    }
    if details is not None:
        data["details"] = details
    return JsonResponse(data, status=400)

@csrf_exempt
@require_POST
def register(request):
    if not request.body:
        return validation_error()

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return validation_error()

    if not body or not isinstance(body, dict):
        return validation_error()

    username = body.get("username")
    password = body.get("password")
    
    details = {}
    if "username" not in body:
        details["username"] = "Falta el campo"
    elif type(username) is not str or not username.strip():
        details["username"] = "Debe ser un string no vacío"
        
    if "password" not in body:
        details["password"] = "Falta el campo"
    elif type(password) is not str or len(password) < 8:
        details["password"] = "Debe ser string de al menos 8 caracteres"

    if details:
        return validation_error(details)

    if User.objects.filter(username=username).exists():
        return validation_error({"username": "El nombre de usuario ya está en uso"})

    user = User.objects.create_user(username=username, password=password)
    
    return JsonResponse({"id": user.id, "username": user.username}, status=201)

@csrf_exempt
@require_POST
def login_view(request):
    if not request.body:
        return validation_error()

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return validation_error()

    if not body or not isinstance(body, dict):
        return validation_error()

    username = body.get("username")
    password = body.get("password")

    details = {}
    if "username" not in body or type(username) is not str:
        details["username"] = "Falta el campo o no es string"
    if "password" not in body or type(password) is not str:
        details["password"] = "Falta el campo o no es string"

    if details:
        return validation_error(details)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        auth_login(request, user)
        return JsonResponse({"id": user.id, "username": user.username}, status=200)
    else:
        return unauthorized_error("Credenciales incorrectas")

@require_GET
def me(request):
    if request.user.is_authenticated:
        return JsonResponse({"id": request.user.id, "username": request.user.username}, status=200)
    else:
        return unauthorized_error("No autenticado")
