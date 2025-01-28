import os
import pathlib
import sys

import dotenv
import urllib3


def is_true_env(env_name, default=None):
    data = os.environ.get(env_name, default)
    if data is None:
        raise ValueError(f"Environment variable {env_name} is not set")

    return str(data).lower() == "true"


def list_env(env_name, default=None):
    data = os.environ.get(env_name, default)
    if data is None:
        raise ValueError(f"Environment variable {env_name} is not set")

    return data.split(",")


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

dotenv.load_dotenv(BASE_DIR / ".env.development")

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = is_true_env("DEBUG")

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

DEFAULT_VERIFED_EMAIL = is_true_env("DEFAULT_VERIFED_EMAIL")

ALLOWED_HOSTS = list_env("ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = list_env("CSRF_TRUSTED_ORIGINS")
CORS_ALLOWED_ORIGINS = list_env("CORS_ALLOWED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "sorl.thumbnail",
    "django_filters",
    "channels",
    "django_elasticsearch_dsl",
    "django_cleanup.apps.CleanupConfig",
    "api.apps.ApiConfig",
    "catalog.apps.CatalogConfig",
    "users.apps.UsersConfig",
    "payments.apps.PaymentsConfig",
    "staff.apps.StaffConfig",
    "core.apps.CoreConfig",
    "telegram_bot.apps.TelegramBotConfig",
    "support.apps.SupportConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "users.middleware.EnsureSessionKeyMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "myproject"),
        "USER": os.getenv("POSTGRES_USER", "myprojectuser"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "password"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/minute",
        "user": "20/minute",
    },
    "EXCEPTION_HANDLER": "backend.exception_handlers.custom_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = os.getenv("DJANGO_INTERNAL_IPS", "127.0.0.1").split(",")
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}

if TESTING:
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}


CSRF_COOKIE_SECURE = is_true_env("CSRF_COOKIE_SECURE", default=False)
SESSION_COOKIE_SECURE = is_true_env("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "Lax")
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_HTTPONLY = is_true_env("CSRF_COOKIE_HTTPONLY", default=False)
SESSION_COOKIE_HTTPONLY = is_true_env("SESSION_COOKIE_HTTPONLY", default=False)


AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = ["users.backends.EmailUsernameBackend"]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 465
EMAIL_USE_SSL = True

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER

LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

STATIC_URL = "static/django/"

STATIC_ROOT = "../staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")


SITE_URL = os.getenv("SITE_URL")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0",
)
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/0",
)
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_ONCE = {
    "backend": "celery_once.backends.Redis",
    "settings": {
        "url": CELERY_BROKER_URL,
        "default_timeout": 60 * 10,
    },
}

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        }
    },
    "handlers": {
        "logstash": {
            "level": "INFO",
            "class": "logstash.TCPLogstashHandler",
            "host": "localhost",
            "port": 5000,
            "version": 1,
            "message_type": "django",
            "fqdn": False,
            "tags": ["django"],
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "grafana": {
            "handlers": ["logstash"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

ELASTICSEARCH_HOST = os.getenv(
    "ELASTICSEARCH_HOST",
    "http://localhost:9200",
)
ELASTICSEARCH_USER = os.getenv(
    "ELASTICSEARCH_USER",
    "elastic",
)
ELASTICSEARCH_PASSWORD = os.getenv(
    "ELASTICSEARCH_PASSWORD",
    "WZNXKNqpcaQtrCigSno9",
)

ELASTICSEARCH_DSL = {
    "default": {
        "hosts": ELASTICSEARCH_HOST,
        "http_auth": (ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
        "verify_certs": False,
    }
}

ELASTICSEARCH_DSL_AUTOSYNC = True
ELASTICSEARCH_DSL_AUTO_REFRESH = True

ASGI_APPLICATION = "backend.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                os.getenv(
                    "CHANNEL_LAYERS_HOST",
                    "redis://localhost:6379/2",
                )
            ],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_CACHE_URL", "redis://localhost:6379/1"),
    }
}
