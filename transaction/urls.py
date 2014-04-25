from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from transaction import views

urlpatterns = patterns(
    '',
    url(r'^init/$', views.TransactionInitialization.as_view(),
        name="transaction-init"),
)

urlpatterns = format_suffix_patterns(urlpatterns)
