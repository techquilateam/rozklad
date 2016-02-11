import os
from .settings_secure import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANONYMOUS_USER_ID = None

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
