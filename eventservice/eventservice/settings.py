from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------
# Core Django Settings
# ---------------------------------------------------------
SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="", cast=Csv())

# ---------------------------------------------------------
# Application definition
# ---------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "eventservice",
    "django_filters",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "eventservice.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "eventservice.wsgi.application"

# ---------------------------------------------------------
# Database
# ---------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", default=BASE_DIR / "db.sqlite3"),
        "USER": config("DB_USER", default=""),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default=""),
        "PORT": config("DB_PORT", default=""),
    }
}


# ---------------------------------------------------------
# Password validation
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------
# Internationalization
# ---------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------
# Static & Media
# ---------------------------------------------------------
STATIC_URL = config("DJANGO_STATIC_URL", default="/static/")
MEDIA_URL = config("DJANGO_MEDIA_URL", default="/media/")
STATIC_ROOT = config("DJANGO_STATIC_ROOT", default=BASE_DIR / "staticfiles")
MEDIA_ROOT = config("DJANGO_MEDIA_ROOT", default=BASE_DIR / "mediafiles")

# ---------------------------------------------------------
# Default primary key field type
# ---------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------
# Django REST Framework & JWT
# ---------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "eventservice.authentication.StatelessJWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

# SimpleJWT
from datetime import timedelta

with open("jwtRS256.key.pub", "r") as f:
    PUBLIC_KEY = f.read()

SIMPLE_JWT = {
    "ALGORITHM": "RS256",
    "VERIFYING_KEY": PUBLIC_KEY,
    "ISSUER": "http://localhost:8000",
    "AUDIENCE": ["http://localhost:8000", "http://localhost:8001"],
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("JWT_ACCESS_TOKEN_LIFETIME", default=5, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        minutes=config("JWT_REFRESH_TOKEN_LIFETIME", default=1440, cast=int)
    ),
    "TOKEN_OBTAIN_SERIALIZER": "eventservice.serializers.MyTokenObtainPairSerializer",
}


# ---------------------------------------------------------
# Email Settings
# ---------------------------------------------------------
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="webmaster@localhost")

# ---------------------------------------------------------
# Caching (Redis Example)
# ---------------------------------------------------------
REDIS_URL = config("REDIS_URL", default="")
REDIS_HOST = config("REDIS_HOST", default="")
REDIS_PORT = config("REDIS_PORT", default="")
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")
REDIS_DB = config("REDIS_DB", default="")
REDIS_USERNAME = config("REDIS_USERNAME", default="")


# ---------------------------------------------------------
# CORS (Cross-Origin Resource Sharing)
# ---------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS", default="http://localhost:3000", cast=Csv()
)


# Internal service communication settings
INTERNAL_SERVICE_IPS = [
    "10.0.1.100",  # Event service IP
    "10.0.1.101",  # Other microservice IPs
    "127.0.0.1",  # For local development
    "localhost",  # For local development
]
