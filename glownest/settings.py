"""
Django settings for GlowNest Beauty Studio.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-change-in-production')

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

# Render deployment: auto-add Render's external hostname
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if '.onrender.com' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('.onrender.com')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third party
    'rest_framework',
    'corsheaders',
    # Project apps
    'services.apps.ServicesConfig',
    'appointments.apps.AppointmentsConfig',
    'dashboard.apps.DashboardConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'glownest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'glownest.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'glownest.wsgi.application'

def sanitize_database_url(url: str) -> str:
    """
    Sanitize database URLs to prevent startup crashes on Render/Supabase:
    - Strips surrounding quotes and whitespace.
    - Strips square brackets from domain hostnames (e.g. @[host]:port or @[host:port]).
      Python's urllib.parse treats [] as IPv6 notation and raises ValueError when
      the bracketed content is a plain hostname. Genuine IPv6 addresses are preserved.
    - Strips square brackets from password or username (e.g. :[YOUR-PASSWORD]@ or :[secret]@)
      which commonly occur when copy-pasting from Supabase connection strings.
    """
    if not url:
        return url
    import re as _re
    url = url.strip().strip("'\"")

    def _clean_host(match):
        prefix = match.group(1) or ''
        host = match.group(2).strip()
        port = (match.group(3) or '').strip()
        if ':' in host and not port:
            h, p = host.split(':', 1)
            return f"{prefix}{h.strip()}:{p.strip()}"
        if port:
            return f"{prefix}{host}:{port}"
        return f"{prefix}{host}"

    # Strip brackets around domain hostnames (with dots/hyphens, not IPv6 colons)
    url = _re.sub(
        r'(@|//)\[\s*([a-zA-Z0-9.\-_]+(?::\d+)?)\s*\](?::(\d+))?',
        _clean_host,
        url,
    )

    # Strip square brackets around password or username
    url = _re.sub(r':\[\s*([^\]@]+?)\s*\]@', r':\1@', url)
    url = _re.sub(r'//\[\s*([^\]@:]+?)\s*\]:', r'//\1:', url)

    return url


# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    _db_url = sanitize_database_url(DATABASE_URL)
    if 'YOUR-PASSWORD' in _db_url:
        import sys
        print(
            '[GlowNest] WARNING: DATABASE_URL still contains placeholder "YOUR-PASSWORD". '
            'Please update the DATABASE_URL environment variable in Render with your actual password.',
            file=sys.stderr,
        )
    try:
        DATABASES = {
            'default': dj_database_url.parse(_db_url, conn_max_age=600, ssl_require=True)
        }
    except Exception as _db_url_err:
        import sys
        print(
            f'[GlowNest] DATABASE_URL could not be parsed: {_db_url_err}\n'
            f'Check that DATABASE_URL in your Render environment is a valid '
            f'postgresql:// URL without brackets.',
            file=sys.stderr,
        )
        raise
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if DEBUG
            else 'whitenoise.storage.CompressedStaticFilesStorage'
        ),
    },
}
WHITENOISE_MANIFEST_STRICT = False

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# CORS settings
_cors_origins_env = os.getenv('CORS_ALLOWED_ORIGINS', '')
if _cors_origins_env:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins_env.split(',') if o.strip()]
else:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]
    if RENDER_EXTERNAL_HOSTNAME:
        CORS_ALLOWED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# CSRF trusted origins for production and Render
_csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if _csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins_env.split(',') if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'https://*.onrender.com',
    ]
    if RENDER_EXTERNAL_HOSTNAME:
        CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# Login URL
LOGIN_URL = '/admin-dashboard/login/'
LOGIN_REDIRECT_URL = '/admin-dashboard/'

# WhatsApp Number
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', '+911234567890')

# Security settings for production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
