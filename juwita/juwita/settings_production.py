from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['juwita.club', 'www.juwita.club']

# Security settings for production
CSRF_TRUSTED_ORIGINS = ['https://juwita.club', 'https://www.juwita.club']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
