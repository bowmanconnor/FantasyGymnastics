from FantasyGymnastics.settings.common import *
import os
import environ

env = environ.Env()
environ.Env.read_env()

DEBUG = False

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = ['104.248.122.140', 'myfgl.com', 'www.myfgl.com']

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_new',
        'USER': 'django',
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

SOCIAL_AUTH_FACEBOOK_KEY = env('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = env('SOCIAL_AUTH_FACEBOOK_SECRET')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
