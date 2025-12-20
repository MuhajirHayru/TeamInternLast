import os
from pathlib import Path
from datetime import timedelta

# ========================
# BASE
# ========================
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "replace-with-a-real-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]
load_dotenv(BASE_DIR / ".env")
# ========================
# INSTALLED APPS
# ========================
INSTALLED_APPS = [
    # Local apps
    "Teamworkapp",

    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Required for SITE_ID

    # Third-party
     "rest_framework.authtoken",

    
    
    "rest_framework_simplejwt",
    "phonenumber_field",
    "channels",  # Channels for real-time WebSocket notifications
]

SITE_ID = 1

AUTH_USER_MODEL = "Teamworkapp.User"



# =========================
# EMAIL SETTINGS (DEV)
# =========================
# settings.py

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django.core.mail": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "bekelegetaneh24@gmail.com"
EMAIL_HOST_PASSWORD = "oreviyfnqkjiajlf"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


ROOT_URLCONF = "TeamIntern.urls"
WSGI_APPLICATION = "TeamIntern.wsgi.application"
 # For WebSocket support

# ========================
# Middleware
# ========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ========================
# Site framework
# ========================


# ========================
# YouTube API Key
# ========================
YOUTUBE_API_KEY = "AIzaSyC9zMR2-L0l0fDSUAw0IstAWdLqozDn2hc"

# ========================
# Templates
# ========================
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

# ========================
# Database
# ========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ========================
# Static & Media
# ========================
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

# ========================
# REST Framework & JWT
# ========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ========================
# Internationalization
# ========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ========================
# Channels: WebSockets & Real-time Notifications
# ========================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",  # Recommended for production
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],  # Redis running locally
        },
    }
}

# ========================
# Optional Settings
# ========================
# CORS if React frontend is hosted separately
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    # Add production frontend URL here
]
