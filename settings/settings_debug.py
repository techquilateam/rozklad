from .settings_secure import *

DEBUG = True

API_DOMAIN = 'api.rozklad-test.hub.kpi.ua'
FRONTEND_DOMAIN = 'rozklad-test.hub.kpi.ua'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rozklad_test',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
