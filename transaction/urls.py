from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from transaction import views


transaction_list = views.TransactionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

transaction_detail = views.TransactionViewSet.as_view({
    'get': 'retrieve',
})

pricing = views.PricingViewSet.as_view({
    'post': 'create'
})

pricing_detail = views.PricingViewSet.as_view({
    'get': 'retrieve',
})

urlpatterns = patterns(
    '',

    # transactions
    url(r'^transaction/$', transaction_list, name='transaction'),
    url(r'^transaction/(?P<pk>[0-9]+)/$', transaction_detail, name='transaction-detail'),
    url(r'^transaction/accept/$', 'transaction.views.accept', name='transaction-accept'),
    url(r'^transaction/accept_status/$', 'transaction.views.get_accept_status', name='transaction-accept-status'),

    # pricing
    url(r'^pricing/$', pricing, name='pricing'),
    url(r'^pricing/(?P<pk>[0-9]+)/$', pricing_detail, name='pricing-detail'),
    url(r'^pricing/current/$', views.PricingCurrent.as_view(), name='pricing-current'),
    url(r'^pricing/local/$', views.PricingLocal.as_view(), name='pricing-local'),

    url(r'^test/$', 'transaction.views.test'),
    url(r'^result/$', 'transaction.views.result'),

)

urlpatterns = format_suffix_patterns(urlpatterns)
