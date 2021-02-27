from FantasyGymnastics.settings.common import *

DEBUG = True

SECRET_KEY = "testing"

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.sqlite3',
       'NAME': BASE_DIR / 'db.sqlite3',
   }
}

SOCIAL_AUTH_FACEBOOK_KEY = '473855363608522'
SOCIAL_AUTH_FACEBOOK_SECRET = '8e9f30f5de45f8e4046773a8d5ae9a0f'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '1060952399049-b64p1fdcd70dpetqs4hb9rfclm3gs46v.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'RBcXLvtnbgOeQBGQXbkC-xXx'