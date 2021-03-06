import requests
from requests import RequestException

import json

from kitiwa.utils import log_error
from payment.utils import MPowerException

from kitiwa.settings import MPOWER_TOKEN, MPOWER_MASTER_KEY,\
    MPOWER_PRIVATE_KEY, MPOWER_ENDPOINT_OPR_TOKEN_REQUEST,\
    MPOWER_ENDPOINT_OPR_TOKEN_CHARGE, MPOWER_ENDPOINT_CHECK_INVOICE_STATUS,\
    MPOWER_RESPONSE_SUCCESS, MPOWER_STATUS_COMPLETED


def _create_headers():
    return {
        'content-type': 'application/json',
        'MP-Master-Key': MPOWER_MASTER_KEY,
        'MP-Private-Key': MPOWER_PRIVATE_KEY,
        'MP-Token': MPOWER_TOKEN
    }


def opr_token_request(amount, mpower_phone_number,
                      invoice_desc='', store_name='Kitiwa'):

    # convert to local phone number format
    mpower_phone_number = '0{}'.format(mpower_phone_number[4::])

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
    try:
        response = requests.post(
            MPOWER_ENDPOINT_OPR_TOKEN_REQUEST,
            data=json.dumps(payload),
            headers=headers
        )

        decoded_response = response.json()
        response_code = decoded_response['response_code']
        response_text = decoded_response['response_text']

        opr_token = decoded_response['token']
        invoice_token = decoded_response['invoice_token']
    except KeyError as e:
        opr_token = invoice_token = 'N/A'
    except RequestException as e:
        message = 'ERROR - MPOWER (opr_token_request for no: {}): {}'
        log_error(message.format(mpower_phone_number, repr(e)))
        response_code = opr_token = invoice_token = 'N/A'
        response_text = repr(e)
    return response_code, response_text, opr_token, invoice_token


def opr_charge_action(opr_token, confirm_token):

    headers = _create_headers()

    payload = {
        'token': opr_token,
        'confirm_token': confirm_token
    }

    try:
        response = requests.post(
            MPOWER_ENDPOINT_OPR_TOKEN_CHARGE,
            data=json.dumps(payload),
            headers=headers
        )

        decoded_response = response.json()

        response_code = decoded_response['response_code']
        response_text = decoded_response['response_text']

    except (RequestException, KeyError) as e:
        message = 'ERROR - MPOWER (opr_charge_action for token {}): {}'
        log_error(message.format(opr_token, repr(e)))
        response_code = "N/A"
        response_text = repr(e)

    return response_code, response_text


def check_invoice_status(invoice_token):

    headers = _create_headers()
    endpoint = MPOWER_ENDPOINT_CHECK_INVOICE_STATUS.format(invoice_token)
    try:
        response = requests.get(
            endpoint,
            headers=headers
        )
        decoded_response = response.json()

        if decoded_response['response_code'] != MPOWER_RESPONSE_SUCCESS:
            message = 'ERROR - MPOWER (check_invoice_status for token {}): transaction not found'
            raise MPowerException

        if decoded_response['status'] != MPOWER_STATUS_COMPLETED:
            message = 'ERROR - MPOWER (check_invoice_status for token {}): transaction not completed'
            raise MPowerException

        return True

    except (RequestException, KeyError, ValueError) as e:
        message = 'ERROR - MPOWER (check_invoice_status for token {}): {}'
        log_error(message.format(invoice_token, repr(e)))
    except MPowerException:
        log_error(message.format(invoice_token))

    return False
