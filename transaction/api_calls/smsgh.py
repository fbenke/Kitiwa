import requests
import re
from requests.auth import HTTPBasicAuth
import json

from kitiwa.settings import SMSGH_CLIENT_ID, SMSGH_CLIENT_SECRET,\
    SMSGH_SEND_MESSAGE, SMSGH_CHECK_BALANCE, SMSGH_USER, SMSGH_PASSWORD

from kitiwa.settings import NOTIFY_USER_CONF_REF_TEXT_SINGLE,\
    NOTIFY_USER_CONF_REF_TEXT_MULTIPLE, NOTIFY_USER_CONF_CALL_TO_ACTION


def send_message(mobile_number, reference_numbers):

    content = _create_confirm_message(reference_numbers)

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

    try:
        message_id = decoded_response['MessageId']
    except KeyError:
        message_id = ''

    return response_status, message_id


def _create_confirm_message(reference_numbers):

    if len(reference_numbers) == 1:
        message = NOTIFY_USER_CONF_REF_TEXT_SINGLE.format(reference_numbers[0])
    else:
        message = NOTIFY_USER_CONF_REF_TEXT_MULTIPLE.format(
            ', #'.join(reference_numbers)
        )

    return '{} {}'.format(message, NOTIFY_USER_CONF_CALL_TO_ACTION)


def check_balance():

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

    return balance
