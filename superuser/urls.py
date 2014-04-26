from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^api/v1/login/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^api/v1/logout/', 'superuser.views.api_logout'),
)
