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

ENV = os.environ.get('ENV')

# ENV names
ENV_LOCAL = 'local'
ENV_DEV = 'dev'
ENV_VIP = 'vip'
ENV_PROD = 'prod'

# Site types in Env
SITE_API = 0
SITE_ADMIN = 1
SITE_USER = 2

# ENV to URL mapping
ENV_SITE_MAPPING = {
    ENV_LOCAL: {
        SITE_API: 'localhost',
        SITE_ADMIN: 'localhost',
        SITE_USER: 'localhost'
    },
    ENV_DEV: {
        SITE_API: 'api-dev.kitiwa.com',
        SITE_ADMIN: 'admin-dev.kitiwa.com',
        SITE_USER: 'dev.kitiwa.com'
    },
    ENV_VIP: {
        SITE_API: 'api-vip.kitiwa.com',
        SITE_ADMIN: 'admin-vip.kitiwa.com',
        SITE_USER: 'vip.kitiwa.com'
    },
    ENV_PROD: {
        SITE_API: 'api.kitiwa.com',
        SITE_ADMIN: 'admin.kitiwa.com',
        SITE_USER: 'kitiwa.com'
    }
}

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
)

LOCAL_APPS = (
    'kitiwa',
    'transaction',
    'superuser',
    'payment',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# SSL Redirects
if ENV != ENV_LOCAL:
    PRODUCTION_MIDDLEWARE = ('sslify.middleware.SSLifyMiddleware',)
else:
    # No automatic redirects on local
    PRODUCTION_MIDDLEWARE = ()

MIDDLEWARE_CLASSES = PRODUCTION_MIDDLEWARE + (
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

# Django Rest Framework
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

# Django CORS headers
if ENV == ENV_LOCAL:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = (
        ENV_SITE_MAPPING[ENV][SITE_ADMIN],
        ENV_SITE_MAPPING[ENV][SITE_USER]
    )

# Proxies
proxies = {
    "http": os.environ['QUOTAGUARDSTATIC_URL']
}

# Site settings
MAXIMUM_AMOUNT_BTC_BUYING = 500

# Bitcoin general settings
ONE_SATOSHI = 100000000
BITCOIN_NOTE = 'Buy bitcoins in Ghana @ http://kitiwa.com'

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
BITSTAMP_API_BUY = BITSTAMP_API_URL + 'buy/'
BITSTAMP_API_TRANSACTIONS = BITSTAMP_API_URL + 'user_transactions/'
BITSTAMP_API_DEFAULT_NUM_TRANSACTIONS = 5
BITSTAMP_API_ORDERS = BITSTAMP_API_URL + 'open_orders/'
BITSTAMP_API_CANCEL_ORDER = BITSTAMP_API_URL + 'cancel_order/'
BITSTAMP_API_WITHDRAW_BTC = BITSTAMP_API_URL + 'bitcoin_withdrawal/'
# SECRETS:
BITSTAMP_CLIENT_ID = os.environ.get('BITSTAMP_CLIENT_ID')
BITSTAMP_API_KEY = os.environ.get('BITSTAMP_API_KEY')
# These can be generated using ./manage.py encryptapisecret
BITSTAMP_ENC_API_SECRET_BASE64 = os.environ.get('BITSTAMP_ENC_API_SECRET_BASE64')
BITSTAMP_ENC_SALT_BASE64 = os.environ.get('BITSTAMP_ENC_SALT_BASE64')
BITSTAMP_ENC_IV_BASE64 = os.environ.get('BITSTAMP_ENC_IV_BASE64')

# Openexchangerate settings
OPEN_EXCHANGE_RATE_API_URL = 'https://openexchangerates.org/api/latest.json?app_id=dc2e5940109a49249841672fa39c7ccd'

# Payment Providers
MPOWER = '0'
PAGA = '1'
PAYMENT_PROVIDERS = (MPOWER, PAGA, )

# Currencies
GHS = '0'
NGN = '1'
CURRENCIES = (GHS, NGN, )

PAYMENT_CURRENCY = {
    MPOWER: GHS,
    PAGA: NGN
}

# Phone Numbers
GH_DIAL_CODE = '+233'
NG_DIAL_CODE = '+234'

DIAL_CODES = (GH_DIAL_CODE, NG_DIAL_CODE,)

PAYMENT_DIAL_CODE = {
    MPOWER: GH_DIAL_CODE,
    PAGA: NG_DIAL_CODE
}

# Mpower Payments
MPOWER_ENDPOINT_OPR_TOKEN_REQUEST = os.environ.get('MPOWER_ENDPOINT_OPR_TOKEN_REQUEST')
MPOWER_ENDPOINT_OPR_TOKEN_CHARGE = os.environ.get('MPOWER_ENDPOINT_OPR_TOKEN_CHARGE')
MPOWER_MASTER_KEY = os.environ.get('MPOWER_MASTER_KEY')
MPOWER_PRIVATE_KEY = os.environ.get('MPOWER_PRIVATE_KEY')
MPOWER_TOKEN = os.environ.get('MPOWER_TOKEN')
MPOWER_RESPONSE_SUCCESS = '00'
MPOWER_RESPONSE_INSUFFICIENT_FUNDS = '3001'
MPOWER_RESPONSE_OTHER_ERROR = '1001'
MPOWER_INVD_ACCOUNT_ALIAS_ERROR_MSG = ('Invalid account alias')
MPOWER_INVD_TOKEN_ERROR_MSG = ('Invalid payment request confirmation token specified')

# Paga Payments
PAGA_MERCHANT_KEY = '96caaff0-2e0c-4bb7-96b4-c1728956ea91'

# Sendgrid Settings
SENDGRID_USERNAME = os.environ.get('SENDGRID_USERNAME')
SENDGRID_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
SENDGRID_EMAIL_FROM = 'noreply@kitiwa.com'

# Smsgh Settings
SMSGH_CLIENT_ID = os.environ.get('SMSGH_CLIENT_ID')
SMSGH_CLIENT_SECRET = os.environ.get('SMSGH_CLIENT_SECRET')
SMSGH_SEND_MESSAGE = 'https://api.smsgh.com/v3/messages'
SMSGH_USER = os.environ.get('SMSGH_USER')
SMSGH_PASSWORD = os.environ.get('SMSGH_PASSWORD')
SMSGH_CHECK_BALANCE = 'http://www.mytxtbox.com/smsghapi.ashx/getbalance'

# Notification Settings
NOTIFY_ADMIN_PAID = bool(int(os.environ.get('NOTIFY_ADMIN_PAID', '1')))
NOTIFY_ADMIN_EMAIL_SUBJECT_PAID = 'Kitiwa: There are transactions waiting to be processed'
NOTIFY_ADMIN_EMAIL_BODY_PAID = \
    '''
    Dear Admin,
    There are transactions on {} waiting to be processed.

    Sincerely,
    The SendGridBot
    '''
NOTIFY_ADMIN_TRANSACTION_THRESHOLD = os.environ.get('NOTIFY_ADMIN_TRANSACTION_THRESHOLD')
NOTIFY_USER_CONF_REF_TEXT_SINGLE = 'Your bitcoin order #{} has been processed!'
NOTIFY_USER_CONF_REF_TEXT_MULTIPLE = 'The following bitcoin orders have been processed: #{}!'
NOTIFY_USER_CONF_CALL_TO_ACTION = 'Please check your bitcoin wallet and confirm that you\'ve received it on our Facebook page: fb.com/kitiwaBTC'
NOTIFY_USER_TOPUP = 'Hello, you\'ve been rewarded {} cedis of phone credit for using Kitiwa. Come back soon! <3 :) http://fb.com/kitiwaBTC'

# Knoxxi Settings
KNOXXI_TOP_UP_ENABLED = bool(int(os.environ.get('KNOXXI_TOP_UP_ENABLED', '1')))
KNOXXI_BASE_URL = 'http://www.corenett.net/Tycoon2/TransactionManager'
KNOXXI_USER_NAME = os.environ.get('KNOXXI_USER_NAME')
KNOXXI_API_KEY = os.environ.get('KNOXXI_API_KEY')
KNOXXI_TOPUP_PERCENTAGE = 0.01
KNOXXI_NETWORK_CODES = {
    # Tigo
    '027': '005',
    '057': '005',
    # MTN
    '024': '004',
    '054': '004',
    # Airtel
    '026': '001',
    # Vodafone
    '020': '007',
    '050': '007',
    # Expresso
    '028': '002',
    # GLO
    '023': '003'
}
