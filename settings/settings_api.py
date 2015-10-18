from .settings import *
from . import domains

ALLOWED_HOSTS = [domains.API_DOMAIN]

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'data',
    'api',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'api.urls'

CORS_ORIGIN_ALLOW_ALL = True
