import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from steamlike_backend.services.email_service import EmailService, EmailServiceError
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_POST
def debug_email_test(request):
    """
    Endpoint for debugging email sending. Only available in DEBUG mode.
    Path: POST /api/debug/email/test/
    """
    if not settings.DEBUG:
        return JsonResponse({"error": "not_found"}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "validation_error", "message": "Invalid JSON"}, status=400)

    # Validations
    to = data.get("to")
    subject = data.get("subject")
    text = data.get("text")

    errors = {}
    if not to: errors["to"] = "Field required"
    elif not isinstance(to, str): errors["to"] = "Must be a string"
    
    if not subject: errors["subject"] = "Field required"
    if not text: errors["text"] = "Field required"

    if errors:
        return JsonResponse({
            "error": "validation_error",
            "fields": errors
        }, status=400)

    # Send email using service
    try:
        EmailService.send_email(
            to=to,
            subject=subject,
            text=text,
            context_info={"action": "debug_test"}
        )
        return JsonResponse({"ok": True}, status=200)
    except EmailServiceError as e:
        return JsonResponse({"error": e.message}, status=e.status_code)
    except Exception as e:
        return JsonResponse({"error": "unexpected_error", "message": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def debug_clear_users(request):
    """
    Ruta: /api/debug/clear-users/
    Endpoint de emergencia para borrar a todos los usuarios de la base de datos
    (excepto superusuarios) cuando no hay acceso a Shell/Admin en Render.
    """
    try:
        # Borramos todos los usuarios que no sean staff/superuser
        users_to_delete = User.objects.filter(is_superuser=False, is_staff=False)
        count = users_to_delete.count()
        users_to_delete.delete()
        
        return JsonResponse({
            "ok": True, 
            "message": f"Se han eliminado {count} usuarios de prueba correctamente."
        }, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
