from django.conf.urls import patterns, url
from superuser.views import ObtainStaffAuthToken

urlpatterns = patterns(
    '',
    url(r'^api/v1/login/', ObtainStaffAuthToken.as_view()),
    url(r'^api/v1/logout/', 'superuser.views.api_logout'),
)
