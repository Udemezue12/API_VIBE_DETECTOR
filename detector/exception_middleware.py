import logging

from django.http import JsonResponse

from .friendly_msg import get_friendly_message

logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            response = self.get_response(request)
            return response

        except Exception as exception:

            trace_id = request.headers.get("X-Request-ID", "none")
            client_ip = request.META.get("REMOTE_ADDR", "unknown")

            logger.error(
                f"[GLOBAL ERROR] TraceID={trace_id} | "
                f"Path={request.path} | "
                f"Method={request.method} | "
                f"Client={client_ip} | "
                f"Error={exception}",
                exc_info=True,
            )

            return JsonResponse(
                {"detail": get_friendly_message(exception)},
                status=500,
            )