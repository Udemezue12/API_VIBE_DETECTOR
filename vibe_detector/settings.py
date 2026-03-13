from pathlib import Path

from django_bolt.auth import AllowAny, JWTAuthentication

from detector.env import (
    ALLOW_DEBUG,
    ALLOWED_ORIGINS,
    CORS_ALLOWED_HOSTS,
    CSRF_TRUSTED_HOSTS,
    JWT_SECRET_KEY,
    REDIS_URL,
)

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = JWT_SECRET_KEY

DEBUG = ALLOW_DEBUG

ALLOWED_HOSTS = ALLOWED_ORIGINS


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "detector",
    "django_bolt",
]

MIDDLEWARE = [
    "detector.exception_middleware.GlobalExceptionMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vibe_detector.urls"
STATIC_URL = "/static/"


STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_DIRS = [
    BASE_DIR / "static",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "vibe_detector.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "casted.db",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 10,
            },
        },
    }
}
BOLT_AUTHENTICATION_CLASSES = [
    JWTAuthentication(),
]


BOLT_DEFAULT_PERMISSION_CLASSES = [
    AllowAny(),
]


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "detector.CustomUser"


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


CELERY_BROKER_URL = REDIS_URL


CELERY_RESULT_BACKEND = REDIS_URL

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_USE_SSL = None
CELERY_REDIS_BACKEND_USE_SSL = None

CELERY_BROKER_POOL_LIMIT = 5
CELERY_REDIS_MAX_CONNECTIONS = 10
CELERY_WORKER_CONCURRENCY = 1
CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_HOSTS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_HOSTS

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
