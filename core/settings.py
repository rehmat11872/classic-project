# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os
from decouple import config
from unipath import Path
from datetime import timedelta
import dj_database_url
if os.name == 'nt':
        import platform
        OSGEO4W = r"C:\OSGeo4W"
        if '64' in platform.architecture()[0]:
            OSGEO4W += "64"
        assert os.path.isdir(OSGEO4W), "Directory does not exist: " + OSGEO4W
        os.environ['OSGEO4W_ROOT'] = OSGEO4W
        os.environ['GDAL_DATA'] = OSGEO4W + r"\share\gdal"
        os.environ['PROJ_LIB'] = OSGEO4W + r"\share\proj"
        os.environ['PATH'] = OSGEO4W + r"\bin;" + os.environ['PATH']
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = Path(__file__).parent
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(config('DEBUG', default=0))
# Force HTTPS
CUSTOM_DEV_MODE = int(config('DEV', default=0))
CUSTOM_STG_MODE = int(config('STG', default=0))
CUSTOM_PROD_MODE = int(config('PROD', default=0))
# load production server from .env
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '103.245.90.20',
    '10.10.128.172',
    'qlassicstg.cidb.gov.my',
    'qlassic.cidb.gov.my',
    'cidb-qlassic.pipe.my',
    'cidb-qlassic.herokuapp.com',
    'localhost:8000',
    'ec32-119-155-25-63.ngrok.io'
]
SITE_ID = config('SITE_ID', default=1)
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django_filters',
    # External Library
    'crispy_forms',
    'qr_code',
    'django_apscheduler',
    'widget_tweaks',
    'absoluteuri',
    # REST
    'anymail',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'phonenumber_field',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    'simple_history',
    # Inner App
    'webapp',
    'api',
    'app',
    'assessments',
    'billings',
    'projects',
    'trainings',
    'users',
    'portal',
    # Django Cleanup - to remove old file if remove/change file related db entry
    'django_cleanup.apps.CleanupConfig',
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]
CRISPY_TEMPLATE_PACK = 'bootstrap4'
ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"   # Route defined in app/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in app/urls.py
TEMPLATE_DIR = [
    os.path.join(BASE_DIR, "core/templates"),  # ROOT dir for templates
    os.path.join(BASE_DIR, "webapp/templates"),  # ROOT dir for templates
    os.path.join(BASE_DIR, "app/templates"),  # ROOT dir for templates
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATE_DIR,
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
WSGI_APPLICATION = 'core.wsgi.application'
# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',#'django_multitenant.backends.postgresql',#'django.contrib.gis.db.backends.postgis',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         'DISABLE_SERVER_SIDE_CURSORS': True
#     }
# }
# import dj_database_url
# db_from_env = dj_database_url.config(default=config('DATABASE_URL'), conn_max_age=500)
# DATABASES['default'].update(db_from_env)
# if any(db_from_env):
#     DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         'DISABLE_SERVER_SIDE_CURSORS': True,
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypass',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
# import dj_database_url
# db_from_env = dj_database_url.config(default=config('DATABASE_URL', default=None), conn_max_age=500)
# DATABASES['default'].update(db_from_env)
# if any(db_from_env):
#     use_mssql = config('USE_MSSQL', default=0)
#     if use_mssql == 1:
#         DATABASES['default']['ENGINE'] = 'sql_server.pyodbc'
#         DATABASES['default']['OPTIONS']['driver'] = 'ODBC Driver 13 for SQL Server'
#     else:
#         DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
# else:
#     SPATIALITE_LIBRARY_PATH='/usr/local/lib/mod_spatialite.dylib'
# Auth User Model
AUTH_USER_MODEL = 'users.CustomUser'
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kuala_Lumpur'
USE_I18N = True
# USE_L10N = True
USE_L10N = False
USE_TZ = True
LANGUAGES = [
    ('en','English'),
    ('ms_MY', 'Malay')
]
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd M Y, H:i'
DATE_INPUT_FORMATS = ('%d/%m/%Y',)
TIME_INPUT_FORMATS = ('%H:%M %p',)
# DATE_INPUT_FORMATS = ('%d/%m/%Y','%Y-%m-%d',)
#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'core/static'),
)
#############################################################
#############################################################
## GEOS Setting
# geo_enabled = config('BUILD_WITH_GEO_LIBRARIES', default=0)
# if geo_enabled == 1:
#     GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH')
#     GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH')
## SendGrid
# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_HOST_USER = 'apikey' # this is exactly the value 'apikey'
# EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = 'noreply@cidb.gov.my'
ANYMAIL = {
    # 'SENDGRID_API_KEY': config('SENDGRID_API_KEY'),
    'SENDGRID_API_KEY': 'dghdhfd3487yerv4',
}
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
DEFAULT_FROM_EMAIL = 'QLASSIC Portal <noreply@cidb.gov.my>'  # if you don't already have this in settings
# AUTH_USER_MODEL = 'users.CustomUser'
# ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[QLASSIC Portal] '
if CUSTOM_DEV_MODE == 0:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = False
    EMAIL_HOST = 'pro.turbo-smtp.com'
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = 587
    if CUSTOM_STG_MODE == 1:
        ACCOUNT_EMAIL_SUBJECT_PREFIX = '[STAGING QLASSIC Portal] '
skip_email = config('SKIP_EMAIL', default=0)
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'https://cidb-qlassic.herokuapp.com',
    'https://cidb-qlassic.pipe.my',
    'https://qlassicstg.cidb.gov.my',
    'https://qlassic.cidb.gov.my',
    'http://127.0.0.1',
    'https://103.245.90.20',
    'https://10.10.128.172',
    'https://localhost:8100',
    'http://localhost'
]
CORS_ORIGIN_REGEX_WHITELIST = [
    'https://cidb-qlassic.herokuapp.com',
    'https://cidb-qlassic.pipe.my',
    'https://qlassicstg.cidb.gov.my',
    'https://qlassic.cidb.gov.my',
    'https://103.245.90.20',
    'https://10.10.128.172',
    'http://127.0.0.1',
    'https://localhost:8100',
    'http://localhost'
]
# Django Storages
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID',default='')
if(AWS_ACCESS_KEY_ID != ''):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL')
    AWS_DEFAULT_ACL = 'public-read'
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
if CUSTOM_DEV_MODE == 0:
    print('live')
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        'qlassicstg.cidb.gov.my',
        'qlassic.cidb.gov.my'
    ]
    ABSOLUTEURI_PROTOCOL = 'https'
else:
    print('dev')
REST_USE_JWT = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'authentication.backends.JWTAuthentication',
    )
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('SECRET_KEY', default='S#perS3crEt_1122'),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
DATA_UPLOAD_MAX_MEMORY_SIZE = 1048576000
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'iamtahir727@gmail.com'
EMAIL_HOST_PASSWORD = 'jvyaysudqpyowece'
EMAIL_USE_TLS = True
MAIL_USE_SSL = True
EMAIL_PORT = 587