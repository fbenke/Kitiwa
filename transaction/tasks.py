from __future__ import absolute_import

from celery import shared_task

from transaction.api_calls import sendgrid_mail


@shared_task
def add(x, y):
    print 'hello'
    return x + y


@shared_task
def accept():
    pass


@shared_task
def notify_admins_paid():
    sendgrid_mail.notify_admins_paid()
