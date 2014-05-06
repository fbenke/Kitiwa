import requests
import re
from requests.auth import HTTPBasicAuth
import json

from kitiwa.settings import SMSGH_CLIENT_ID, SMSGH_CLIENT_SECRET,\
    SMSGH_CONTENT, SMSGH_SEND_MESSAGE, SMSGH_CHECK_BALANCE,\
    SMSGH_USER, SMSGH_PASSWORD


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

    try:
        message_id = decoded_response['MessageId']
    except KeyError:
        message_id = ''

    return response_status, message_id


def check_smsgh_balance():

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
