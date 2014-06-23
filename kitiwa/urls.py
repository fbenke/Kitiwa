from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, RedirectView
from django.contrib import admin
from kitiwa.settings import STATIC_URL

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(
        r'^$',
        TemplateView.as_view(template_name='index.html'),
        name='home'
    ),
    url(
        r'^robots\.txt$',
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain'),
        name='robots'
    ),
    url(
        r'^humans\.txt$',
        TemplateView.as_view(template_name='humans.txt', content_type='text/plain'),
        name='humans'
    ),
    url(
        r'^favicon\.ico$',
        RedirectView.as_view(url=STATIC_URL + 'img/favicon.ico')
    ),
    url(
        r'^api/v1/superuser/',
        include('superuser.urls', namespace='superuser')
    ),
    url(
        r'^api/v1/',
        include('transaction.urls', namespace='transaction')
    ),
    url(
        r'^admin/',
        include(admin.site.urls)),
    url(
        r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
)

handler404 = 'kitiwa.views.page_not_found'
handler500 = 'kitiwa.views.custom_error'
handler403 = 'kitiwa.views.permission_denied'
handler400 = 'kitiwa.views.bad_request'
