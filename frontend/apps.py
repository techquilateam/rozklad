from django.apps import AppConfig
from django.core.cache import caches

class FrontendConfig(AppConfig):
    name = 'frontend'
    verbose_name= 'Frontend'

    def ready(self):
        cache = caches['default']
        cache.clear()
