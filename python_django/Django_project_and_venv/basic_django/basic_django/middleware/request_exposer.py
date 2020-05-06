from django.conf import settings
from basic_django import settings as settings_basic_django

def RequestExposerMiddleware(get_response):
    def middleware(request):
        settings_basic_django.exposed_request = request
        response = get_response(request)
        return response

    return middleware