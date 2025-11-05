from pathlib import Path
import environ
import os
from datetime import timedelta

# -----------------------------------------------------------------------------
# Base
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# env setup
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "insecure-default"),
    ALLOWED_HOSTS=(str, "127.0.0.1,localhost,10.0.0.82"),
    DATABASE_URL=(str, "sqlite:///db.sqlite3"),
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))  # reads backend/.env

DEBUG = env.bool("DEBUG")
SECRET_KEY = env.str("SECRET_KEY")
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "10.0.0.82",
]

# -----------------------------------------------------------------------------
# Installed apps
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "medicalcoder",
    "corsheaders",
]

AUTH_USER_MODEL = "medicalcoder.User"

# -----------------------------------------------------------------------------
# Middleware / Templates (default)
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend_core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "backend_core.wsgi.application"

# -----------------------------------------------------------------------------
# Database (sqlite now; env DATABASE_URL controls it)
# -----------------------------------------------------------------------------
# Simple sqlite resolver
db_url = env.str("DATABASE_URL")
if db_url.startswith("sqlite:///"):
    default_db = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / db_url.replace("sqlite:///", ""),
    }
else:
    # You can parse other DB URLs later (MSSQL etc.)
    # For MSSQL you’ll switch ENGINE and OPTIONS in Phase 9.
    default_db = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

DATABASES = {"default": default_db}

# -----------------------------------------------------------------------------
# Password validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Static files
# -----------------------------------------------------------------------------
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------------
# DRF + JWT
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "EXCEPTION_HANDLER": "medicalcoder.exception_handler.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django": {"handlers": ["console"], "level": "INFO"},
    },
}
# -----------------------------------------------------------------------------  
# CORS (Cross-Origin Resource Sharing)  
# -----------------------------------------------------------------------------  
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# If your internal frontend IP is different (e.g. 192.168.x.x:5173 or your PC hostname)
# you can add it too:
# "http://192.168.1.10:5173",
# "http://pc-1f-00037.appedology.internal:5173",

CORS_ALLOW_CREDENTIALS = False  # not using cookies, only tokens

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
