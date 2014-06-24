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
    url(r'^transaction/opr_charge/$', views.TransactionOprCharge.as_view(), name='transaction-charge'),

    # pricing
    url(r'^pricing/$', pricing, name='pricing'),
    url(r'^pricing/(?P<pk>[0-9]+)/$', pricing_detail, name='pricing-detail'),
    url(r'^pricing/current/$', views.PricingCurrent.as_view(), name='pricing-current'),
    url(r'^pricing/ghs/$', views.PricingGHS.as_view(), name='pricing-ghs'),

    # paga tests
    url(r'^paga/return/$', 'transaction.views.page_test_backend', name='paga-test'),
    url(r'^paga/redirect/$', 'transaction.views.page_test_frontend', name='paga-test'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
