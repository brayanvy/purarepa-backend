import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this settings file
load_dotenv(dotenv_path=Path(__file__).resolve().parent / '.env')

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'rest_framework', 'rest_framework_simplejwt', 'corsheaders',
    'accounts', 'products', 'orders', 'reports'
]
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware', 'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'src.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'src.wsgi.application'

import dj_database_url
# DATABASES = {'default': dj_database_url.config(default=f'postgres://postgres:postgres@localhost:5432/purarepa_db', conn_max_age=600, ssl_require=not DEBUG)}
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}]
LANGUAGE_CODE, TIME_ZONE = 'es-co', 'America/Bogota'
USE_I18N, USE_TZ = True, True
STATIC_URL, STATIC_ROOT = 'static/', BASE_DIR / 'staticfiles'
MEDIA_URL, MEDIA_ROOT = 'media/', BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination', 'PAGE_SIZE': 20
}
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8501').split(',')
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=86400),
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=604800),
}
MP_ACCESS_TOKEN = os.getenv('MP_ACCESS_TOKEN', '')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8501')