"""
Django settings for TicketReservation project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv('DEBUG') or False)
ALLOWED_HOSTS = [host for host in os.getenv('ALLOWED_HOSTS').replace('"', '').replace("'", '').split(',')]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'tickets.apps.TicketsConfig',
    'users.apps.UsersConfig',
    'stadiums.apps.StadiumsConfig',
    'matches.apps.MatchesConfig',
    'rest_framework',
    'django_filters',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

WSGI_APPLICATION = 'TicketReservation.wsgi.application'

AUTH_USER_MODEL = 'users.User'
ROOT_URLCONF = 'TicketReservation.urls'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {},

    'users': {
        'NAME': 'newsbox_users',
        'USER': 'root',
        'PASSWORD': '1',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.1.105',
        'PORT': 3306
    },

    'tickets': {
        'NAME': 'newsbox_tickets',
        'USER': 'root',
        'PASSWORD': '1',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.1.105',
        'PORT': 3306
    },
    'matches': {
        'NAME': 'newsbox_matches',
        'USER': 'root',
        'PASSWORD': '1',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.1.105',
        'PORT': 3306
    },
    'stadiums': {
        'NAME': 'newsbox_stadiums',
        'USER': 'root',
        'PASSWORD': '1',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.1.105',
        'PORT': 3306
    },

}

DATABASE_ROUTERS = ['tickets.db_router.TicketsDBRouter', 'users.db_router.UsersDBRouter',
                    'stadiums.db_router.StadiumsDBRouter', 'matches.db_router.MatchesDBRouter']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
#
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'users.renderers.ApiRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'TicketReservation.middleware.MyTokenAuthentication',
    ]
}

MATCH_DIFFERENCE_TIME = int(os.getenv('MATCH_DIFFERENCE_TIME'))

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
