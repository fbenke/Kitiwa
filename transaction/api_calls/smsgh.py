import requests
import re
from requests.auth import HTTPBasicAuth
from requests import RequestException
from kitiwa.utils import log_error
import json

from kitiwa.settings import SMSGH_CLIENT_ID, SMSGH_CLIENT_SECRET,\
    SMSGH_SEND_MESSAGE, SMSGH_CHECK_BALANCE, SMSGH_USER, SMSGH_PASSWORD

from kitiwa.settings import NOTIFY_USER_CONF_REF_TEXT_SINGLE,\
    NOTIFY_USER_CONF_REF_TEXT_MULTIPLE, NOTIFY_USER_CONF_CALL_TO_ACTION

from kitiwa.settings import NOTIFY_USER_TOPUP, KNOXXI_TOP_UP_ENABLED


def send_message_confirm(mobile_number, reference_numbers):

    if len(reference_numbers) == 1:
        message = NOTIFY_USER_CONF_REF_TEXT_SINGLE.format(reference_numbers[0])
    else:
        message = NOTIFY_USER_CONF_REF_TEXT_MULTIPLE.format(
            ', #'.join(reference_numbers)
        )

    content = '{} {}'.format(message, NOTIFY_USER_CONF_CALL_TO_ACTION)

    return _send_message(mobile_number, content)


def send_message_topup(mobile_number, topup):

    if not KNOXXI_TOP_UP_ENABLED:
        return

    content = NOTIFY_USER_TOPUP.format(topup)

    return _send_message(mobile_number, content)


def _send_message(mobile_number, content):

    # convert phone number to match expected format by smsgh
    mobile_number = '+233{}'.format(mobile_number[1::])

    headers = {
        'content-type': 'application/json',
        'Host': 'api.smsgh.com'
    }

    payload = {
        'From': 'Kitiwa',
        'To': mobile_number,
        'Content': content,
        'RegisteredDelivery': 'true'
    }
    try:

        response = requests.post(
            SMSGH_SEND_MESSAGE,
            data=json.dumps(payload),
            headers=headers,
            auth=HTTPBasicAuth(SMSGH_CLIENT_ID, SMSGH_CLIENT_SECRET)
        )

        decoded_response = response.json()

        response_status = decoded_response['Status']

        message_id = decoded_response['MessageId']

    except (RequestException, KeyError) as e:
        message = 'ERROR - SMSGH: Failed to send message to {}.({}).'
        log_error(message.format(mobile_number, repr(e)))
        message_id = response_status = 'N/A'

    return response_status, message_id


def check_balance():

    payload = {
        'api_id': SMSGH_CLIENT_ID,
        'user': SMSGH_USER,
        'password': SMSGH_PASSWORD
    }
    try:
        response = requests.get(
            SMSGH_CHECK_BALANCE,
            params=payload
        )

        balance = float(re.search(r'\d+.\d+', response.text).group(0))
    except (RequestException, IndexError) as e:
        message = 'ERROR - SMSGH: Failed to check balance ({}).'
        log_error(message.format(repr(e)))
        return

    return balance
