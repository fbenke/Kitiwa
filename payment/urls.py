from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from payment.views import general


urlpatterns = patterns(
    '',

    # payments
    url(r'^(?P<pk>[0-9]+)/$', general.RetrievePayment.as_view(), name='payment-detail'),

    # mpower
    url(r'^mpower/$', 'payment.views.mpower.opr_charge', name='mpower-charge'),

    # paga
    url(r'^paga/backendcallback/$', 'payment.views.paga.backend_callback', name='paga-backend-callback'),
    url(r'^paga/usercallback/$', 'payment.views.paga.user_callback', name='paga-user-callback'),

)

urlpatterns = format_suffix_patterns(urlpatterns)
