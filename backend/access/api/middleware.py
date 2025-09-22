from access.api.exceptions import ObjectAccessDeniedError
from django.http import JsonResponse
from utils.utils import ValidationError


class ErrorHandlerMiddleware:
    """Middleware для перехвата исключений."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, ObjectAccessDeniedError):
            status = getattr(exception, 'status', 403)
            return JsonResponse(
                {'error': str(exception)},
                status=status
            )

        elif isinstance(exception, ValidationError):
            status = getattr(exception, 'status', 400)
            return JsonResponse(
                {'error': str(exception)},
                status=status
            )

        return None