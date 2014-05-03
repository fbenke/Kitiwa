import os

import dj_database_url


# Helpers

BASE_DIR = lambda *x: os.path.join(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)).replace('\\', '/'), *x)

# From Environment Variables
DEBUG = bool(int(os.environ.get('DEBUG', '1')))

TEMPLATE_DEBUG = bool(int(os.environ.get('TEMPLATE_DEBUG', '1')))

SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ['*']

# Application definition
DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'gunicorn',
    'south',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_extensions',
)

LOCAL_APPS = (
    'kitiwa',
    'transaction',
    'superuser',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)

ROOT_URLCONF = 'kitiwa.urls'

WSGI_APPLICATION = 'kitiwa.wsgi.application'


# Database
DATABASES = {
    'default': dj_database_url.config()
}

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files
STATIC_ROOT = 'static'

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    BASE_DIR('assets'),
)

# Templates
TEMPLATE_DIRS = (
    BASE_DIR('templates'),
)

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
        }
    }
}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1/second'
    }
}


'''
TODO: This should be changed when the site goes live. Only the
domains of the angular apps should be allowed using CORS_ORIGIN_WHITELIST
'''
CORS_ORIGIN_ALLOW_ALL = True


# Bitcoin general settings
ONE_SATOSHI = 100000000
BITCOIN_NOTE = 'Buy Bitcoins in Ghana @ http://kitiwa.com Exchange Rate: {rate}, ' + \
               'Source: Blockchain Exchange Rates Feed, Timestamp: {time} UTC'

# Blockchain settings
BLOCKCHAIN_GUID = os.environ.get('BLOCKCHAIN_GUID')
BLOCKCHAIN_API_URL = 'https://blockchain.info/merchant/' + BLOCKCHAIN_GUID
BLOCKCHAIN_API_BALANCE = BLOCKCHAIN_API_URL + '/balance/'
BLOCKCHAIN_API_SENDMANY = BLOCKCHAIN_API_URL + '/sendmany/'
BLOCKCHAIN_TICKER = 'https://blockchain.info/ticker'
BLOCKCHAIN_TRANSACTION_FEE_SATOSHI = 50000


# Bitstamp settings
BITSTAMP_API_URL = 'https://www.bitstamp.net/api/'
BITSTAMP_API_TICKER = BITSTAMP_API_URL + 'ticker/'
BITSTAMP_API_BALANCE = BITSTAMP_API_URL + 'balance/'
# SECRETS:
BITSTAMP_CLIENT_ID = os.environ.get('BITSTAMP_CLIENT_ID')
BITSTAMP_API_KEY = os.environ.get('BITSTAMP_API_KEY')
# These can be generated using ./manage.py encryptapisecret
BITSTAMP_ENC_API_SECRET_BASE64 = os.environ.get('BITSTAMP_ENC_API_SECRET_BASE64')
BITSTAMP_ENC_SALT_BASE64 = os.environ.get('BITSTAMP_ENC_SALT_BASE64')
BITSTAMP_ENC_IV_BASE64 = os.environ.get('BITSTAMP_ENC_IV_BASE64')


# Openexchangerate settings
OPEN_EXCHANGE_RATE_API_URL = 'https://openexchangerates.org/api/latest.json?app_id=dc2e5940109a49249841672fa39c7ccd'


# MPower settings
MPOWER_ENDPOINT_OPR_TOKEN_REQUEST = os.environ.get('MPOWER_ENDPOINT_OPR_TOKEN_REQUEST')
MPOWER_ENDPOINT_OPR_TOKEN_CHARGE = os.environ.get('MPOWER_ENDPOINT_OPR_TOKEN_CHARGE')
MPOWER_MASTER_KEY = os.environ.get('MPOWER_MASTER_KEY')
MPOWER_PRIVATE_KEY = os.environ.get('MPOWER_PRIVATE_KEY')
MPOWER_TOKEN = os.environ.get('MPOWER_TOKEN')

# Sendgrid Settings
SENDGRID_ACTIVATE = bool(int(os.environ.get('SENDGRID_ACTIVATE', '1')))
if SENDGRID_ACTIVATE:
    SENDGRID_USERNAME = os.environ.get('SENDGRID_USERNAME')
    SENDGRID_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
    SENDGRID_TRANSACTION_THRESHOLD = os.environ.get('SENDGRID_TRANSACTION_THRESHOLD')
    SENDGRID_EMAIL_FROM = 'noreply@kitiwa.com'
    SENDGRID_EMAIL_SUBJECT = 'Kitiwa: There are transactions waiting to be processed'
    SENDGRID_EMAIL_BODY =\
        '''
        Dear Admin,
        there are transactions waiting to be processed.

        Sincerely,
        the SendGridBot
        '''
