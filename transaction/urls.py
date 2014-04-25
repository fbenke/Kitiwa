from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from transaction import views

urlpatterns = patterns(
    '',
    url(r'^transaction/$', views.TransactionAPI.as_view(),
        name='transaction'),

)

urlpatterns = format_suffix_patterns(urlpatterns)
