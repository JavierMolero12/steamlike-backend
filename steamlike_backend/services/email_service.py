import requests
import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)

class EmailServiceError(Exception):
    """Base exception for EmailService"""
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ExternalServiceUnavailable(EmailServiceError):
    """Error 503: Network or timeout issues"""
    def __init__(self, message="external_service_unavailable"):
        super().__init__(message, 503)

class ExternalServiceError(EmailServiceError):
    """Error 502: Provider returned error or invalid response"""
    def __init__(self, message="external_service_error"):
        super().__init__(message, 502)

class EmailService:
    API_URL = "https://api.maileroo.com/v1/transactional/send"

    @staticmethod
    def send_email(to, subject, text, html=None, context_info=None):
        """
        Sends an email using Maileroo API.
        :param to: Recipient email address
        :param subject: Email subject
        :param text: Plain text content
        :param html: Optional HTML content
        :param context_info: Dict with context for logging (action, user_id, etc.)
        """
        api_key = os.getenv("MAILEROO_API_KEY")
        from_email = os.getenv("MAILEROO_FROM_EMAIL")
        from_name = os.getenv("MAILEROO_FROM_NAME", "Steamlike")

        context_info = context_info or {}
        action = context_info.get('action', 'send_email')
        user_info = f" | User: {context_info.get('user_id')}" if 'user_id' in context_info else ""

        logger.info(f"Attempting to send email | Action: {action}{user_info} | To: {to}")

        if not api_key or not from_email:
            logger.error("Email service configuration missing (API Key or From Email)")
            raise ExternalServiceError("configuration_missing")

        payload = {
            "from_name": from_name,
            "from_email": from_email,
            "to": to,
            "subject": subject,
            "plain_text": text,
        }
        if html:
            payload["html_content"] = html

        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(EmailService.API_URL, json=payload, headers=headers, timeout=10)
            
            if response.status_code >= 500:
                logger.error(f"Fallo por respuesta del proveedor | Action: {action} | Status: {response.status_code} | To: {to}")
                raise ExternalServiceError()
            
            if response.status_code != 200:
                logger.warning(f"Respuesta inválida del proveedor | Action: {action} | Status: {response.status_code} | Body: {response.text} | To: {to}")
                raise ExternalServiceError()

            data = response.json()
            if not data.get("success"):
                logger.warning(f"Maileroo reportó error | Action: {action} | Message: {data.get('error')} | To: {to}")
                raise ExternalServiceError()

            logger.info(f"Envío OK | Action: {action} | To: {to}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Fallo por timeout/red | Action: {action} | Error: {str(e)} | To: {to}")
            raise ExternalServiceUnavailable()
        except Exception as e:
            if isinstance(e, EmailServiceError):
                raise e
            logger.error(f"Error inesperado en servicio de email | Error: {str(e)}")
            raise ExternalServiceError()
