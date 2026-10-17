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
    'django.contrib.sites',
    'django.contrib.sitemaps',
    # Third party
    'rest_framework',
    'corsheaders',
    # Project apps
    'services.apps.ServicesConfig',
    'appointments.apps.AppointmentsConfig',
    'dashboard.apps.DashboardConfig',
    'api.apps.ApiConfig',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'glownest.views.DiagnosticExceptionMiddleware',
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
    - Strips surrounding quotes, backticks, angle brackets (<>), and outer square brackets ([]).
    - Safely parses authority (userinfo and hostinfo) even if userinfo contains brackets or special characters.
    - Strips square brackets from domain hostnames (e.g. @[host]:port or @[host:port]).
      Python's urllib.parse treats [] as IPv6 notation and raises ValueError when
      the bracketed content is a plain hostname. Genuine IPv6 addresses are preserved.
    - Strips square brackets from username and password (e.g. postgres.[project-ref]:[YOUR-PASSWORD]@
      or [user]:[secret]@), which commonly occur when copy-pasting from Supabase connection strings.
    - Safely percent-encodes passwords with reserved characters (like @, [, ], #, ?) so that
      urllib.parse does not misinterpret them as host or scheme separators.
    - Strips brackets from database name (e.g. /[postgres]).
    - Automatically routes Supabase pooler connections (pooler.supabase.com) to transaction mode (port 6543)
      if port 5432 or no port is specified, preventing EMAXCONNSESSION pool exhaustion.
    """
    if not url:
        return url

    clean = url.strip()
    while (
        (clean.startswith('"') and clean.endswith('"')) or
        (clean.startswith("'") and clean.endswith("'")) or
        (clean.startswith('`') and clean.endswith('`')) or
        (clean.startswith('<') and clean.endswith('>')) or
        (clean.startswith('[') and clean.endswith(']'))
    ):
        clean = clean[1:-1].strip()

    if clean.startswith('sqlite:') or clean.startswith('sqlite://'):
        return clean

    import re as _re
    import ipaddress as _ipaddress
    import urllib.parse as _urlparse

    # Separate scheme
    if '://' in clean:
        scheme, rest = clean.split('://', 1)
    else:
        scheme = 'postgresql'
        rest = clean

    # Determine authority and the rest (path, query, fragment)
    # The authority is terminated by the first '/' in rest.
    if '/' in rest:
        authority, pqf = rest.split('/', 1)
        pqf = _re.sub(r'^\[\s*([^\]]+?)\s*\]', r'\1', pqf)
        path_query_fragment = '/' + pqf
    else:
        if '@' in rest:
            pre_at, post_at = rest.rsplit('@', 1)
            m = _re.search(r'[?#]', post_at)
            if m:
                host_part = post_at[:m.start()]
                path_query_fragment = post_at[m.start():]
                authority = f"{pre_at}@{host_part}"
            else:
                authority = rest
                path_query_fragment = ''
        else:
            m = _re.search(r'[?#]', rest)
            if m:
                authority = rest[:m.start()]
                path_query_fragment = rest[m.start():]
            else:
                authority = rest
                path_query_fragment = ''

    # Separate userinfo and hostinfo (the last '@' separates credentials from host)
    if '@' in authority:
        userinfo, hostinfo = authority.rsplit('@', 1)
        has_userinfo = True
    else:
        userinfo = ''
        hostinfo = authority
        has_userinfo = False

    # Clean userinfo (user:password)
    clean_userinfo = ''
    if has_userinfo:
        if ':' in userinfo:
            raw_user, raw_pass = userinfo.split(':', 1)
            clean_user = _re.sub(r'\[\s*([^\]]+?)\s*\]', r'\1', raw_user.strip())

            clean_pass = raw_pass.strip()
            if clean_pass.startswith('[') and clean_pass.endswith(']'):
                clean_pass = clean_pass[1:-1].strip()

            unquoted_pass = _urlparse.unquote(clean_pass)
            safe_pass = _urlparse.quote(unquoted_pass, safe='')

            unquoted_user = _urlparse.unquote(clean_user)
            safe_user = _urlparse.quote(unquoted_user, safe='.')
            clean_userinfo = f'{safe_user}:{safe_pass}@'
        else:
            clean_user = _re.sub(r'\[\s*([^\]]+?)\s*\]', r'\1', userinfo.strip())
            safe_user = _urlparse.quote(_urlparse.unquote(clean_user), safe='.')
            clean_userinfo = f'{safe_user}@'

    # Clean hostinfo
    hostinfo = hostinfo.strip()
    is_ipv6_literal = False
    clean_host = ''
    clean_port = ''

    if hostinfo.startswith('['):
        bracket_content, _, after_bracket = hostinfo[1:].partition(']')
        bracket_content = bracket_content.strip()
        try:
            ip = _ipaddress.ip_address(bracket_content)
            if isinstance(ip, _ipaddress.IPv6Address):
                is_ipv6_literal = True
        except ValueError:
            is_ipv6_literal = False

        if is_ipv6_literal:
            clean_host = f'[{bracket_content}]'
            clean_port = after_bracket.lstrip(':').strip()
        else:
            if ':' in bracket_content:
                clean_host, clean_port = bracket_content.rsplit(':', 1)
            else:
                clean_host = bracket_content
                clean_port = after_bracket.lstrip(':').strip()
    else:
        if ':' in hostinfo:
            clean_host, clean_port = hostinfo.rsplit(':', 1)
        else:
            clean_host = hostinfo
            clean_port = ''

    if not is_ipv6_literal:
        clean_host = clean_host.strip().strip('[]')
    clean_port = clean_port.strip().strip('[]')

    # Supabase pooler handling: auto-route to transaction mode (port 6543)
    if 'pooler.supabase.com' in clean_host:
        if clean_port == '5432' or not clean_port:
            clean_port = '6543'

    port_str = f':{clean_port}' if clean_port else ''
    return f'{scheme}://{clean_userinfo}{clean_host}{port_str}{path_query_fragment}'


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
    if 'project-ref' in _db_url or 'YOUR-PROJECT-REF' in _db_url:
        import sys
        print(
            '[GlowNest] WARNING: DATABASE_URL contains placeholder "project-ref". '
            'Please update the DATABASE_URL environment variable in Render with your actual Supabase project reference.',
            file=sys.stderr,
        )
    try:
        DATABASES = {
            'default': dj_database_url.parse(
                _db_url,
                conn_max_age=0,
                conn_health_checks=True,
                disable_server_side_cursors=True,
                ssl_require=True,
            )
        }
    except Exception as _db_url_err:
        import sys
        print(
            f'[GlowNest] DATABASE_URL parsing warning via dj_database_url: {_db_url_err}',
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

# Canonical public domain used by the sitemap.
# Set SITE_DOMAIN in Render's environment variables to the exact live URL
# hostname (without protocol or trailing slash) to ensure /sitemap.xml
# always emits the correct absolute URLs, regardless of RENDER_EXTERNAL_HOSTNAME.
SITE_DOMAIN = os.getenv('SITE_DOMAIN', 'beautyparlourbooking-2.onrender.com')

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
