from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^api/login/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^api/logout/', 'superuser.views.api_logout'),
)
