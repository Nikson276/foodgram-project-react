from http import HTTPStatus

from django.http import JsonResponse


class Handle404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == HTTPStatus.NOT_FOUND:
            return JsonResponse(
                {'error': 'Not found'},
                status=HTTPStatus.NOT_FOUND
            )
        return response
