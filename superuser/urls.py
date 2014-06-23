from django.conf.urls import patterns, url
from superuser.views import auth, blockchain, bitstamp, forex


urlpatterns = patterns(
    '',
    # Auth
    url(r'^login/$', auth.Login.as_view()),
    url(r'^logout/$', auth.logout),

    # Blockchain
    url(r'^blockchain/balance/$', blockchain.get_balance),
    url(r'^blockchain/rate/$', blockchain.get_rate),

    # Bitstamp
    url(r'^bitstamp/rate/$', bitstamp.get_rate),
    url(r'^bitstamp/data/$', bitstamp.get_request_data),
    url(r'^bitstamp/balance/$', bitstamp.Balance.as_view()),
    url(r'^bitstamp/orders/$', bitstamp.Orders.as_view()),
    url(r'^bitstamp/order/$', bitstamp.OrderBtc.as_view()),
    url(r'^bitstamp/order/cancel/$', bitstamp.CancelOrder.as_view()),
    url(r'^bitstamp/withdraw/$', bitstamp.Withdraw.as_view()),
    url(r'^bitstamp/transactions/$', bitstamp.Transactions.as_view()),

    # Forex
    url(r'^forex/usd/ghs/$', forex.get_usd_ghs),
)
