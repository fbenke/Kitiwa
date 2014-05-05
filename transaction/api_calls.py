import requests
from requests.auth import HTTPBasicAuth
import json
import sendgrid
import re

from django.contrib.auth.models import User
from transaction.models import Transaction

from kitiwa.settings import MPOWER_TOKEN, MPOWER_MASTER_KEY,\
    MPOWER_PRIVATE_KEY, MPOWER_ENDPOINT_OPR_TOKEN_REQUEST,\
    MPOWER_ENDPOINT_OPR_TOKEN_CHARGE
from kitiwa.settings import NOTIFY_ADMIN_PAID, SENDGRID_USERNAME,\
    SENDGRID_PASSWORD, SENDGRID_EMAIL_FROM, SENDGRID_TRANSACTION_THRESHOLD,\
    SENDGRID_EMAIL_SUBJECT_PAID, SENDGRID_EMAIL_BODY_PAID
from kitiwa.settings import NOTIFY_ADMIN_SMSGH_CREDIT,\
    SENDGRID_EMAIL_SUBJECT_SMSGH,\
    SENDGRID_EMAIL_BODY_SMSGH, SMSGH_CLIENT_ID, SMSGH_CLIENT_SECRET,\
    SMSGH_CONTENT, SMSGH_SEND_MESSAGE, SMSGH_CHECK_BALANCE,\
    SMSGH_USER, SMSGH_PASSWORD, SMSGH_CREDIT_THRESHOLD


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


def _send_mail(subject, body):

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

    _send_mail(SENDGRID_EMAIL_SUBJECT_PAID, SENDGRID_EMAIL_BODY_PAID)


def send_message(mobile_number, reference_number):

    content = SMSGH_CONTENT.format(reference_number)

    # convert phone number to match expected format by smsgh
    mobile_number = '+233{}'.format(mobile_number[1::])

    headers = {
        'content-type': 'application/json',
        'Host': 'api.smsgh.com'
    }

    payload = {
        'From': 'kitiwa',
        'To': mobile_number,
        'Content': content,
        'RegisteredDelivery': 'true'
    }

    response = requests.post(
        SMSGH_SEND_MESSAGE,
        data=json.dumps(payload),
        headers=headers,
        auth=HTTPBasicAuth(SMSGH_CLIENT_ID, SMSGH_CLIENT_SECRET)
    )

    decoded_response = response.json()

    response_status = decoded_response['Status']

    # if response_status == '402':
    #     raise Http500('You ran out of smsgh credits.')

    try:
        message_id = decoded_response['MessageId']
    except KeyError:
        message_id = ''

    return response_status, message_id


def check_smsgh_balance():
    if not NOTIFY_ADMIN_SMSGH_CREDIT:
        return

    payload = {
        'api_id': SMSGH_CLIENT_ID,
        'user': SMSGH_USER,
        'password': SMSGH_PASSWORD
    }

    response = requests.get(
        SMSGH_CHECK_BALANCE,
        params=payload
    )

    try:
        balance = float(re.search(r'\d+.\d+', response.text).group(0))
    except IndexError:
        # TODO: Logging
        return

    if balance < int(SMSGH_CREDIT_THRESHOLD):
        _send_mail(SENDGRID_EMAIL_SUBJECT_SMSGH, SENDGRID_EMAIL_BODY_SMSGH)
