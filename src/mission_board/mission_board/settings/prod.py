import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': os.environ.get('DB_HOSTNAME', 'mb_db'),
        'PORT': 5432,
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "/var/www/mission_board/static")
# ]

STATIC_URL = '/static/'

STATIC_ROOT = "/var/www/mb/static/"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

MEDIA_ROOT = os.path.join(BASE_DIR, '/mb_media')
