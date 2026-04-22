# library/auth_views.py - Gestión de Usuarios y Autenticación

@csrf_exempt
@require_POST
def register(request):
    """
    Ruta: /api/auth/register/
    Crea un nuevo usuario en la plataforma.
    """
    body, error_response = parse_json_body(request)
    if error_response: return error_response

    username = body.get("username")
    password = body.get("password")
    
    # Validaciones básicas de registro
    details = {}
    if "username" not in body:
        details["username"] = "Falta el campo"
    elif type(username) is not str or not username.strip():
        details["username"] = "Debe ser un string no vacío"
        
    if "password" not in body:
        details["password"] = "Falta el campo"
    elif type(password) is not str or len(password) < 8:
        details["password"] = "Debe ser string de al menos 8 caracteres"

    if details: return validation_error(details)

    # Comprobar si el nombre de usuario ya existe
    if User.objects.filter(username=username).exists():
        return validation_error({"username": "El nombre de usuario ya está en uso"})

    # Crear el usuario (Django encripta la contraseña automáticamente)
    user = User.objects.create_user(username=username, password=password)
    return JsonResponse({"id": user.id, "username": user.username}, status=201)

@csrf_exempt
@require_POST
def login_view(request):
    """
    Ruta: /api/auth/login/
    Inicia sesión y crea una cookie de sesión en el navegador.
    """
    body, error_response = parse_json_body(request)
    if error_response: return error_response

    username = body.get("username")
    password = body.get("password")

    # Intentar autenticar al usuario
    user = authenticate(request, username=username, password=password)
    if user is not None:
        auth_login(request, user) # Crea la sesión
        return JsonResponse({"id": user.id, "username": user.username}, status=200)
    else:
        return unauthorized_error("Credenciales incorrectas")

@csrf_exempt
@require_GET
def manage_me(request):
    """
    Ruta: /api/users/me/
    Devuelve la información del perfil del usuario que está logueado.
    """
    if not request.user.is_authenticated:
        return unauthorized_error()
    
    return JsonResponse({"id": request.user.id, "username": request.user.username}, status=200)

@csrf_exempt
@require_POST
def logout_view(request):
    """
    Ruta: /api/auth/logout/
    Ejercicio 6: Cierra la sesión del usuario.
    Devuelve 204 No Content.
    """
    if request.user.is_authenticated:
        auth_logout(request) # Borra la sesión
    return HttpResponse(status=204)

@csrf_exempt
@require_POST
def change_password(request):
    """
    Ruta: /api/users/me/password/
    Ejercicio 2: Permite al usuario cambiar su contraseña actual.
    """
    if not request.user.is_authenticated:
        return unauthorized_error()

    body, error_response = parse_json_body(request)
    if error_response: return error_response

    current_password = body.get("current_password")
    new_password = body.get("new_password")

    # Validaciones del cambio de password
    details = {}
    # Comprobar si la contraseña actual es correcta
    if not current_password or not request.user.check_password(current_password):
        details["current_password"] = "Contraseña actual incorrecta"
    
    # Comprobar longitud de la nueva contraseña
    if not new_password or len(str(new_password)) < 8:
        details["new_password"] = "La nueva contraseña debe tener al menos 8 caracteres"

    if details: return validation_error(details)

    # Cambiar contraseña y guardar
    request.user.set_password(new_password)
    request.user.save()
    
    # Es necesario volver a loguear al usuario tras cambiar password para no perder la sesión
    auth_login(request, request.user)
    
    return JsonResponse({"ok": True}, status=200)
