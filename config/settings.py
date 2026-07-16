"""
Django settings for the GSD HQ LMS.

Everything deployment-specific is driven by environment variables so the same
image runs locally and on the Raspberry Pi behind the Cloudflare Tunnel.
See .env.example / README for the full list.
"""
import os
from pathlib import Path

from django.templatetags.static import static

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")
DEBUG = env_bool("DEBUG", False)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
# e.g. CSRF_TRUSTED_ORIGINS=https://learn.getshtdonehq.com
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# Data directory: holds the SQLite DB and uploaded media. In Docker this is a
# mounted volume (the external drive); locally it defaults to ./data.
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

INSTALLED_APPS = [
    # django-unfold (modern admin theme) must come before contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db.sqlite3",
        # Friendlier defaults for SQLite under a small multi-worker gunicorn.
        "OPTIONS": {
            "timeout": 20,
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
            "transaction_mode": "IMMEDIATE",
        },
    }
}

AUTH_USER_MODEL = "core.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Manila")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Uploaded files (lesson worksheets, student submissions). Served only through
# permission-checked views — MEDIA_URL is never exposed directly.
MEDIA_ROOT = DATA_DIR / "media"
MEDIA_URL = "/protected-media/"

# Student worksheet uploads: max size (MB) and allowed extensions.
SUBMISSION_MAX_MB = int(os.environ.get("SUBMISSION_MAX_MB", "20"))
SUBMISSION_ALLOWED_EXTENSIONS = ["pdf", "png", "jpg", "jpeg", "doc", "docx"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Email (password reset). Defaults to console output; set SMTP vars in prod.
# ---------------------------------------------------------------------------
if os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ["EMAIL_HOST"]
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "GSD HQ <no-reply@getshtdonehq.com>")

# ---------------------------------------------------------------------------
# Security — the app sits behind a Cloudflare Tunnel that terminates HTTPS
# and forwards plain HTTP to the container.
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"

OTP_TOTP_ISSUER = "GSD HQ"

# ---------------------------------------------------------------------------
# django-unfold — modern admin theme, styled to the GSD brand.
# ---------------------------------------------------------------------------
UNFOLD = {
    "SITE_TITLE": "GSD HQ Admin",
    "SITE_HEADER": "GSD HQ",
    "SITE_SUBHEADER": "Mission Control",
    "SITE_URL": "/",
    "SITE_SYMBOL": "school",  # Material icon shown when no logo fits
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SITE_LOGO": {
        "light": lambda request: static("img/logo.png"),
        "dark": lambda request: static("img/logo.png"),
    },
    "COLORS": {
        # GSD Orange (#FF5C00) as the primary accent, full 50–950 scale.
        "primary": {
            "50": "255 241 230",
            "100": "255 226 204",
            "200": "255 197 153",
            "300": "255 168 102",
            "400": "255 130 51",
            "500": "255 92 0",
            "600": "230 82 0",
            "700": "191 69 0",
            "800": "153 55 0",
            "900": "122 44 0",
            "950": "71 26 0",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}
