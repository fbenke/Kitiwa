import requests
import json
import sendgrid

from django.contrib.auth.models import User
from transaction.models import Transaction

from kitiwa.settings import MPOWER_TOKEN, MPOWER_MASTER_KEY,\
    MPOWER_PRIVATE_KEY, MPOWER_ENDPOINT_OPR_TOKEN_REQUEST,\
    MPOWER_ENDPOINT_OPR_TOKEN_CHARGE
from kitiwa.settings import SENDGRID_USERNAME, SENDGRID_PASSWORD,\
    SENDGRID_EMAIL_SUBJECT, SENDGRID_EMAIL_FROM, SENDGRID_EMAIL_BODY,\
    SENDGRID_TRANSACTION_THRESHOLD


def _create_headers():
    return {
        'content-type': 'application/json',
        'MP-Master-Key': MPOWER_MASTER_KEY,
        'MP-Private-Key': MPOWER_PRIVATE_KEY,
        'MP-Token': MPOWER_TOKEN
    }


# TODO: what to send as invoice description?
def opr_token_request(amount, mpower_phone_number,
                      invoice_desc='', store_name='Kitiwa'):

    payload = {
        'invoice_data': {
            'invoice': {
                'total_amount': amount,
                'description': invoice_desc
            },
            'store': {
                'name': store_name
            }
        },
        'opr_data': {
            'account_alias': mpower_phone_number
        }
    }

    headers = _create_headers()

    response = requests.post(
        MPOWER_ENDPOINT_OPR_TOKEN_REQUEST,
        data=json.dumps(payload),
        headers=headers
    )

    decoded_response = response.json()
    response_code = decoded_response['response_code']
    response_text = decoded_response['response_text']

    try:
        opr_token = decoded_response['token']
        invoice_token = decoded_response['invoice_token']
    except KeyError:
        opr_token = invoice_token = ''

    return response_code, response_text, opr_token, invoice_token


def opr_charge_action(opr_token, confirm_token):

    headers = _create_headers()

    payload = {
        'token': opr_token,
        'confirm_token': confirm_token
    }

    response = requests.post(
        MPOWER_ENDPOINT_OPR_TOKEN_CHARGE,
        data=json.dumps(payload),
        headers=headers
    )

    decoded_response = response.json()

    response_code = decoded_response['response_code']
    response_text = decoded_response['response_text']

    try:
        receipt_url = decoded_response['invoice_data']['receipt_url']
    except KeyError:
        receipt_url = ''

    return response_code, response_text, receipt_url


def notify_admins():
    print(Transaction.objects.filter(state=Transaction.PAID).count())
    if Transaction.objects.filter(state=Transaction.PAID).count() < \
            int(SENDGRID_TRANSACTION_THRESHOLD):
        return

    sg = sendgrid.SendGridClient(SENDGRID_USERNAME, SENDGRID_PASSWORD)

    recipients = User.objects.filter(is_staff=True)
    mails = [m.email for m in recipients]

    message = sendgrid.Mail()
    message.add_to(mails)
    message.set_subject(SENDGRID_EMAIL_SUBJECT)
    message.set_from(SENDGRID_EMAIL_FROM)
    message.set_text(SENDGRID_EMAIL_BODY)

    try:
        sg.send(message, raise_errors=True)
    except sendgrid.SendGridError:
        # todo get logging in place
        pass
