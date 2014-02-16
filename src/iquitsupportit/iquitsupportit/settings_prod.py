from iquitsupportit.settings import *

DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['.helpmequ.it',
                 '.iquitsupport.us',
                 ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'la_base_des_dons',
        'USER': 'le_plus_fumeur',
        'PASSWORD': 'yoighImAmNojLetFagCisulp',
        'HOST': '',
        'PORT': '',
    }
}

EMAIL_HOST = 'localhost'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'contact@helpmequ.it'
EMAIL_HOST_PASSWORD = 'W|X<pud!j:oW17R7`6E,8GVT'
EMAIL_USE_TLS = True

AWS_STORAGE_BUCKET_NAME = 'helpmequit-users'
