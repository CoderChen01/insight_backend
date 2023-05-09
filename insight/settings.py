import os
import sys
from datetime import timedelta

from celery.schedules import crontab

from . import local_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "5-6h1n(0nmyei(t6+dl9pz%t-6c2!h99^t516tk4(ev8xsla=8"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "user.apps.UserConfig",
    "interface.apps.InterfaceConfig",
    "camera.apps.CameraConfig",
    "face.apps.FaceConfig",
    "incident.apps.IncidentConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "django_celery_beat",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = "insight.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "")],
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

WSGI_APPLICATION = "insight.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "insight",
        "USER": local_settings.MYSQL_USER,
        "PASSWORD": local_settings.MYSQL_PASSWORD,
        "HOST": local_settings.MYSQL_HOST,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True


USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"


# the following is custom settings

# Set medis files
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


# Set auth model
AUTH_USER_MODEL = "user.UserProfile"


# The REST settings
REST_FRAMEWORK = {
    # Set a custom exception handler that can return a beautiful error response in the event of a json load error
    "EXCEPTION_HANDLER": "rest_tools.custom_exception_handler.custom_exception_handler",
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "DEFAULT_THROTTLE_RATES": {"email": "20/h"},
}


# Set simple_jwt settings
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(days=7)}


# About sending email whose function is in 'django.core.mail'
EMAIL_HOST = local_settings.EMAIL_HOST
EMAIL_PORT = local_settings.EMAIL_PORT
EMAIL_HOST_USER = local_settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = local_settings.EMAIL_HOST_PASSWORD
FROM_EAMIL = local_settings.FROM_EAMIL
# The following two configuration items are about encryption
EMAIL_USE_TLS = local_settings.EMAIL_USE_TLS
# EMAIL_USE_SSL


# The database address that stores the mapping between the email and the captcha
EMAIL_CAPTCHA_MAP_CACHE = local_settings.EMAIL_CAPTCHA_MAP_CACHE
REDIS_THROTTLE_CACHE = local_settings.REDIS_THROTTLE_CACHE
REDIS_CHECK_TASK_STATE = local_settings.REDIS_CHECK_TASK_STATE
REDIS_TASK_QUEUE = local_settings.REDIS_TASK_QUEUE
UPDATE_EMAIL_CAPTCHA_KEY_NAME = "update_email_captcha"
REGISTER_EMAIL_CAPTCHA_KEY_NAME = "register_email_captcha"
FORGOT_PASSWORD_CAPTCHA_KEY_NAME = "forgot_password_email_captcha"

# celery settings
CELERY_BROKER_URL = local_settings.CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
# CELERY_RESULT_BACKEND = 'redis://insight-api-insight_redis-1:6379/1'
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_ENABLE_UTC = False
CELERY_BEAT_SCHEDULE = {
    "clear_incidents": {
        "task": "incident.tasks.clear_incidents",
        "schedule": crontab(minute=0, hour=0, day_of_month="1"),
    }
}
DJANGO_CELERY_BEAT_TZ_AWARE = False

# default auto field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
