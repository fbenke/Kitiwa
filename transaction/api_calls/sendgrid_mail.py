import sendgrid
from kitiwa.settings import NOTIFY_ADMIN_PAID, SENDGRID_EMAIL_SUBJECT_PAID,\
    SENDGRID_EMAIL_BODY_PAID, SENDGRID_TRANSACTION_THRESHOLD

from kitiwa.settings import SENDGRID_USERNAME,\
    SENDGRID_PASSWORD, SENDGRID_EMAIL_FROM

from django.contrib.auth.models import User
from transaction.models import Transaction


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
    except sendgrid.SendGridError:
        # todo get logging in place
        pass


def notify_admins_paid():

    if not NOTIFY_ADMIN_PAID:
        return

    if Transaction.objects.filter(state=Transaction.PAID).count() <\
            int(SENDGRID_TRANSACTION_THRESHOLD):
        return

    send_mail_to_admins(SENDGRID_EMAIL_SUBJECT_PAID, SENDGRID_EMAIL_BODY_PAID)
