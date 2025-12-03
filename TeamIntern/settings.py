import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "replace-with-a-real-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ========================
# INSTALLED APPS
# ========================
INSTALLED_APPS = [
    # Local app
    "Teamworkapp",  # MUST match folder name exactly (capital T)
    
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "phonenumber_field",
]

# ========================
# Custom User Model
# ========================
AUTH_USER_MODEL = "Teamworkapp.User"  # MUST match app folder name

# ========================
# URL and WSGI
# ========================
ROOT_URLCONF = "TeamIntern.urls"          # MUST match project folder name
WSGI_APPLICATION = "TeamIntern.wsgi.application"  # MUST match project folder name

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
# Static and Media
# ========================
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

# ========================
# REST Framework
# ========================
# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": (
#         "rest_framework_simplejwt.authentication.JWTAuthentication",
#     ),
#     "DEFAULT_PERMISSION_CLASSES": (
#         "rest_framework.permissions.IsAuthenticatedOrReadOnly",
#     ),
# }

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
