import sendgrid
from kitiwa.settings import NOTIFY_ADMIN_PAID,\
    NOTIFY_ADMIN_EMAIL_SUBJECT_PAID, NOTIFY_ADMIN_EMAIL_BODY_PAID,\
    NOTIFY_ADMIN_TRANSACTION_THRESHOLD

from kitiwa.settings import SENDGRID_USERNAME,\
    SENDGRID_PASSWORD, SENDGRID_EMAIL_FROM

from kitiwa.settings import ENV, ENV_SITE_MAPPING, SITE_ADMIN

from django.contrib.auth.models import User
from transaction.models import Transaction
from kitiwa.utils import log_error


def send_mail_to_admins(subject, body):

    sg = sendgrid.SendGridClient(SENDGRID_USERNAME, SENDGRID_PASSWORD)

    recipients = User.objects.filter(is_staff=True)
    mails = [m.email for m in recipients]

    message = sendgrid.Mail()
    message.add_to(mails)
    message.set_from(SENDGRID_EMAIL_FROM)
    message.set_subject(subject)
    message.set_text(body)

    try:
        sg.send(message)
    except sendgrid.SendGridError as e:
        log_error('ERROR - Sendgrid: Failed to send mail to admins ({})'.format(e))
        pass


def notify_admins_paid():

    if not NOTIFY_ADMIN_PAID:
        return

    if Transaction.objects.filter(state=Transaction.PAID).count() <\
            int(NOTIFY_ADMIN_TRANSACTION_THRESHOLD):
        return

    message = NOTIFY_ADMIN_EMAIL_BODY_PAID.format(ENV_SITE_MAPPING[ENV][SITE_ADMIN])

    send_mail_to_admins(NOTIFY_ADMIN_EMAIL_SUBJECT_PAID, message)
