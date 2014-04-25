from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^robots\.txt$', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain'), name='robots'),
    url(r'^humans\.txt$', TemplateView.as_view(
        template_name='humans.txt', content_type='text/plain'), name='humans'),
    url(r'^superuser/', include('superuser.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
