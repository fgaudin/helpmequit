"""
Django settings for iquitsupportit project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'skp&%n68!v!s1pzv##u#n32pqwnrgq52&!c7vpw!u!%tfhav*z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost:10001']
SITENAME = "Help Me Quit"
ADMINS = (('Francois Gaudin', 'contact@helpmequ.it'),)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'south',
    'storages',
    'quitter',
    'supporter',
    'donation',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'iquitsupportit.urls'

WSGI_APPLICATION = 'iquitsupportit.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'iquitsupportit',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages",
                               "context_processors.settings_variables")

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

DEFAULT_FROM_EMAIL = 'Help Me Quit <contact@helpmequ.it>'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_DEBUG = False

if not EMAIL_DEBUG:
    EMAIL_HOST = 'mail.gandi.net'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'contact@helpmequ.it'
    EMAIL_HOST_PASSWORD = 'W|X<pud!j:oW17R7`6E,8GVT'
    EMAIL_USE_TLS = True

EMAIL_SIGNATURE = 'The Help Me Quit Team'

DEFAULT_PROFILE = 'francois'

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'auth.backends.TokenBackend',)

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAJZHQWOAUZLNWQ7KQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'test-helpmequit-users'
