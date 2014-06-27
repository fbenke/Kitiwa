from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns(
    '',

    # mpower
    url(r'^mpower/$', 'payment.views.opr_charge', name='transaction-charge'),
    url(r'^paga/usercallback/$', 'payment.views.paga_user_callback', name='paga-user-callback'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
