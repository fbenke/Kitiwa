from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from transaction import views


transaction_list = views.TransactionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

snippet_detail = views.TransactionViewSet.as_view({
    'get': 'retrieve',
})

pricing = views.PricingViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = patterns(
    '',
    url(r'^transaction/$', transaction_list, name='transaction'),
    url(r'^transaction/(?P<pk>[0-9]+)/$', snippet_detail,
        name='transaction-detail'),
    url(r'^pricing/$', pricing,
        name='pricing'),
    url(r'^transaction/accept/$', 'transaction.views.accept',
        name='transaction-accept'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
