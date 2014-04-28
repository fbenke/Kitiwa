from django.conf.urls import patterns, url

from superuser.views import ObtainStaffAuthToken


urlpatterns = patterns(
    '',
    url(r'^api/v1/login/$', ObtainStaffAuthToken.as_view()),
    url(r'^api/v1/logout/$', 'superuser.views.api_logout'),
    url(r'^api/v1/blockchain/balance/$', 'superuser.views.get_blockchain_balance'),
    url(r'^api/v1/bitstamp/rate/$', 'superuser.views.get_bitstamp_rate'),
    url(r'^api/v1/forex/usd/ghs/$', 'superuser.views.get_openexchangerate_usd_ghs'),
)
