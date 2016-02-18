from .settings_secure import *

DEBUG = False

API_DOMAIN = 'api.rozklad.hub.kpi.ua'
FRONTEND_DOMAIN = 'rozklad.hub.kpi.ua'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rozklad',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
