from django.conf.urls import patterns, url
from superuser.views import auth, blockchain, bitstamp, forex


urlpatterns = patterns(
    '',
    # Auth
    url(r'^api/v1/login/$', auth.Login.as_view()),
    url(r'^api/v1/logout/$', auth.logout),

    # Blockchain
    url(r'^api/v1/blockchain/balance/$', blockchain.get_balance),
    url(r'^api/v1/blockchain/rate/$', blockchain.get_rate),

    # Bitstamp
    url(r'^api/v1/bitstamp/rate/$', bitstamp.get_rate),
    url(r'^api/v1/bitstamp/data/$', bitstamp.get_request_data),
    url(r'^api/v1/bitstamp/balance/$', bitstamp.get_balance),

    # Forex
    url(r'^api/v1/forex/usd/ghs/$', forex.get_usd_ghs),
)
