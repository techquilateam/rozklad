from django.conf import settings
from django.utils.cache import patch_vary_headers

class MultiHostMiddleware:
    def process_request(self, request):
        try:
            host = request.META["HTTP_HOST"]
            if host[-3:] == ":80":
                host = host[:-3]
            request.urlconf = settings.HOST_MIDDLEWARE_URLCONF_MAP[host]
        except KeyError:
            pass

    def process_response(self, request, response):
        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))
        return response
