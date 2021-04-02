import sys
import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5-6h1n(0nmyei(t6+dl9pz%t-6c2!h99^t516tk4(ev8xsla=8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user.apps.UserConfig',
    'interface.apps.InterfaceConfig',
    'camera.apps.CameraConfig',
    'face.apps.FaceConfig',
    'incident.apps.IncidentConfig',
    'corsheaders',
    'django_celery_beat'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'insight.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'insight.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'insight',
        'USER': 'root',
        'PASSWORD': 'insight@666',
        'HOST': '192.168.68.134'
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'


# the following is custom settings

# Set medis files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Set auth model
AUTH_USER_MODEL = 'user.UserProfile'


# The REST settings
REST_FRAMEWORK = {
    # Set a custom exception handler that can return a beautiful error response in the event of a json load error
    'EXCEPTION_HANDLER': 'rest_tools.custom_exception_handler.custom_exception_handler',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'email': '20/h'
    }
}


# Set simple_jwt settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7)
}


# About sending email whose function is in 'djano.core.mail'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'coderchen01@qq.com'
EMAIL_HOST_PASSWORD = 'vcppfhsxnrdjigeg'
FROM_EAMIL = 'insight-test<coderchen01@qq.com>'
# The following two configuration items are about encryption
# EMAIL_USE_TLS
# EMAIL_USE_SSL


# The database address that stores the mapping between the email and the captcha
EMAIL_CAPTCHA_MAP_CACHE = 'redis://192.168.68.134:6379/2'
REDIS_THROTTLE_CACHE = 'redis://192.168.68.134:6379/3'
REDIS_CHECK_TASK_STATE = 'redis://192.168.68.134:6379/4'
REDIS_TASK_QUEUE = 'redis://192.168.68.134:6379/5'
UPDATE_EMAIL_CAPTCHA_KEY_NAME = 'update_email_captcha'
REGISTER_EMAIL_CAPTCHA_KEY_NAME = 'register_email_captcha'
FORGOT_PASSWORD_CAPTCHA_KEY_NAME = 'forgot_password_email_captcha'

# celery settings
CELERY_BROKER_URL = 'redis://192.168.68.134:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'redis://192.168.68.134:6379/1'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = False
DJANGO_CELERY_BEAT_TZ_AWARE = False