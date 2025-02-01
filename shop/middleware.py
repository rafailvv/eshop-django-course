# USER -> HTTP REQUEST -> MIDDLEWARE -> HANDLER -> MIDDLEWARE -> HTTP RESPONSE -> USER
import logging

from django.http.response import JsonResponse


logger = logging.getLogger(__name__)


class DiscountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.discount = True
        else:
            request.discount = False

        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.error(f"EXCEPTION ON PATH {request.path} - {str(exception)}")
        if isinstance(exception, ValueError):
            return JsonResponse({"detail": "Cart doesn't exists."}, status=404)
        return None
