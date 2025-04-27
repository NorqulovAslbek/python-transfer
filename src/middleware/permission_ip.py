import os

from django.http import HttpResponseForbidden

ALLOWED_IPS = os.getenv('ALLOWED_IPS', '').split(',')


class PermissionIpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith('/admin/'):
            ip = request.META.get("REMOTE_ADDR")
            if ip not in ALLOWED_IPS:
                return HttpResponseForbidden("Admin panelga kirishga ruxsat yo'q!")
        return self.get_response(request)
