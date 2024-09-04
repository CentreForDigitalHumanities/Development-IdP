"""
Django settings for testidp project.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from . import env

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.get(
    "DJANGO_SECRET_KEY",
    default="django-insecure-lb=q@u4df-x0th(5u%$eye_ti#etst+5z+%2=lrh$$le3&v_y$",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.get_boolean("DJANGO_DEBUG", default=True)
ENABLE_DEBUG_TOOLBAR = env.get_boolean("DJANGO_DEBUG_TOOLBAR", default=DEBUG)
HOSTED = env.get_boolean("DJANGO_HOSTED", default=False)  # Only set to true on
# idp.dev.im.hum.uu.nl
ALLOWED_HOSTS = []

_env_hosts = env.get("DJANGO_ALLOWED_HOSTS", default=None)
if _env_hosts:
    ALLOWED_HOSTS += _env_hosts.split(",")


# Application definition
INSTALLED_APPS = [
    # CDH Core
    "cdh.core",
    # Django supplied apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djangosaml2idp",
    # Django extensions
    "django_extensions",
    # django-simple-menu
    "menu",
    # Impersonate
    "impersonate",
    # Django model translation
    "modeltranslation",
    # Local apps
    "main",
    "idp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

if DEBUG and ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append(
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )

ROOT_URLCONF = "testidp.urls"

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
                "main.context_processors.hosted",
            ],
        },
    },
]

WSGI_APPLICATION = "testidp.wsgi.application"

# Email
# TODO: Decide if to set up email backend
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

_db_type = env.get("DJANGO_DB_TYPE", default="sqlite3")

if _db_type == "sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": env.get("DJANGO_SQLLITE_FILE", default=BASE_DIR / "db.sqlite3"),
        }
    }
elif _db_type == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env.get("POSTGRES_DB", default="idp"),
            "USER": env.get("POSTGRES_USER", default="idp"),
            "PASSWORD": env.get("POSTGRES_PASSWORD", default="idp"),
            "HOST": env.get("POSTGRES_HOST", default="localhost"),
            "PORT": env.get("POSTGRES_PORT", default="5432"),
        }
    }

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth info

AUTH_USER_MODEL = "main.User"

LOGIN_URL = reverse_lazy("main:login")

LOGIN_REDIRECT_URL = reverse_lazy("main:home")


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

PASSWORD_HASHERS = [
    "main.password_hashers.PlainPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGES = (("en", _("lang:en")),)

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "public/static/"

# Security
# https://docs.djangoproject.com/en/2.0/topics/security/

_https_enabled = env.get_boolean("DJANGO_HTTPS", default=False)

X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = _https_enabled

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = _https_enabled
CSRF_COOKIE_SECURE = _https_enabled
# Needed to work in kubernetes, as the app may be behind a proxy/may not know it's
# own domain
SESSION_COOKIE_DOMAIN = env.get("SESSION_COOKIE_DOMAIN", default=None)
CSRF_COOKIE_DOMAIN = env.get("CSRF_COOKIE_DOMAIN", default=None)
SESSION_COOKIE_NAME = env.get("SESSION_COOKIE_NAME", default="devidp_sessionid")
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 12  # 12 hours

CSRF_TRUSTED_ORIGINS = [
    f"http{'s' if _https_enabled else ''}://{host}" for host in ALLOWED_HOSTS
]

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env.get("LOG_LEVEL", default="WARNING"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env.get("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "saml2": {
            "handlers": ["console"],
            "level": env.get("SAML_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "djangosaml2": {
            "handlers": ["console"],
            "level": env.get("SAML_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "djangosaml2idp": {
            "handlers": ["console"],
            "level": env.get("SAML_LOG_LEVEL", default="INFO"),
            "propagate": False,
        }
    },
}

# Django CSP
# http://django-csp.readthedocs.io/en/latest/index.html
CSP_REPORT_ONLY = True
CSP_UPGRADE_INSECURE_REQUESTS = _https_enabled
CSP_INCLUDE_NONCE_IN = ["script-src"]
CSP_EXCLUDE_URL_PREFIXES = ("/idp",)

CSP_DEFAULT_SRC = [
    "'self'",
]
CSP_SCRIPT_SRC = [
    "'self'",
]
CSP_FONT_SRC = [
    "'self'",
    "data:",
]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", "data:", "*"]  # Remove the last one if you
# want to be really secure

# Django Simple Menu
# https://django-simple-menu.readthedocs.io/en/latest/index.html

MENU_SELECT_PARENTS = True
MENU_HIDE_EMPTY = False

try:
    from .saml_settings import *
except Exception as e:
    print("Could not load SAML settings somehow?")
    raise e
