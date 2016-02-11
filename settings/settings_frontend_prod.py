from .settings_frontend import *
from .settings_prod import *

ALLOWED_HOSTS = [FRONTEND_DOMAIN]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'unix:/var/run/memcached.sock',
        'KEY_PREFIX': 'PROD',
    }
}
