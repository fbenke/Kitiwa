from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitiwa.settings')

app = Celery('kitiwa')

app.config_from_object('django.conf:settings')

# lambda makes the list callable to enable lazy evaluation
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
