from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns(
    '',

    # mpower
    url(r'^mpower/$', 'payment.views.opr_charge', name='transaction-charge'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
