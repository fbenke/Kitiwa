from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from payment import views


urlpatterns = patterns(
    '',

    # payments
    url(r'^(?P<pk>[0-9]+)/$', views.RetrievePayment.as_view(), name='payment-detail'),

    # mpower

    url(r'^mpower/$', 'payment.views.opr_charge', name='mpower-charge'),
    url(r'^paga/usercallback/$', 'payment.views.paga_user_callback', name='paga-user-callback'),

)

urlpatterns = format_suffix_patterns(urlpatterns)
