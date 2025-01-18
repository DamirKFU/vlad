import os
from django.http import HttpResponse
from django.conf import settings

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        maintenance_mode = os.getenv('MAINTENANCE_MODE', 'false').lower() == 'true'
        
        if maintenance_mode and not request.path.startswith('/admin'):
            return HttpResponse(
                'Выполняются технические работы', 
                status=503,
                content_type='text/plain; charset=utf-8'
            )
        
        return self.get_response(request) 