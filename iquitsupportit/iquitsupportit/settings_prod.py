from iquitsupportit.settings import *

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['.helpmequ.it',
                 '.iquitsupport.us',
                 '.url-de-test.ws'
                 ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'la_base_des_dons',
        'USER': 'le_plus_fumeur',
        'PASSWORD': 'yoighImAmNojLetFagCisulp',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'helpmequit'
EMAIL_HOST_PASSWORD = 'bluk0jrekIsjefEldIdf3fop'
EMAIL_USE_TLS = True

AWS_STORAGE_BUCKET_NAME = 'helpmequit-users'
