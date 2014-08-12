from __future__ import absolute_import

import requests

from celery import shared_task

from django.db import transaction as dbtransaction
from django.utils import timezone

from transaction import utils
from transaction.models import Transaction
from transaction.api_calls import smsgh
from transaction.utils import AcceptException

from superuser.views.blockchain import get_blockchain_exchange_rate

from kitiwa.settings import BITCOIN_NOTE
from kitiwa.settings import BLOCKCHAIN_API_SENDMANY
from kitiwa.utils import log_error


@shared_task
def add(x, y):
    print 'hello'
    return x + y


@shared_task
def process_transactions(ids, password1, password2):
# TODO: handling results for this?
# TODO: security concerns sending pw1, pw2?
# TODO: need to make this a transaction for atomicity or isolation?

    try:
        transactions = Transaction.objects.select_for_update().filter(id__in=ids)
    except Transaction.DoesNotExist:
        log_error('ERROR - ACCEPT: Invalid ID')
        return

    try:
        with dbtransaction.atomic():

            # Verify payment with payment provider
            for t in transactions:
                if not t.verify_payment():
                    raise AcceptException(
                        'ERROR - ACCEPT: Transaction {} could not be verified as paid'.format(t.id)
                    )

            # Make sure that there are enough credits in smsgh account to send out confirmation sms
            smsgh_balance = smsgh.check_balance()

            if smsgh_balance is None:
                raise AcceptException('ERROR - ACCEPT: Failed to query smsgh balance')
            elif smsgh_balance < len(transactions):
                raise AcceptException('ERROR - ACCEPT: Not enough credit on SMSGH account')

            # USD-BTC CONVERSION
            # Get latest exchange rate
            rate = get_blockchain_exchange_rate()
            if rate is None:
                raise AcceptException('ERROR - ACCEPT: Failed to retrieve exchange rate')

            # Update amount_btc based on latest exchange rate
            for t in transactions:
                t.update_btc(rate)

            # Combine transactions with same wallet address
            combined_transactions = utils.consolidate_transactions(transactions)

            # Prepare request and send
            recipients = utils.create_recipients_string(combined_transactions)

            btc_transfer_request = requests.get(BLOCKCHAIN_API_SENDMANY, params={
                'password': password1,
                'second_password': password2,
                'recipients': recipients,
                'note': BITCOIN_NOTE
            })

            if btc_transfer_request.json().get('error'):
                raise AcceptException('ERROR - ACCEPT (btc transfer request to blockchain): {}'.format(btc_transfer_request.json()))

            transactions.update(state=Transaction.PROCESSED, processed_at=timezone.now())

            combined_sms_confirm = utils.consolidate_notification_sms(transactions)

            # send out confirmation SMS
            for number, reference_numbers in combined_sms_confirm.iteritems():
                response_status, message_id = smsgh.send_message_confirm(
                    mobile_number=number,
                    reference_numbers=reference_numbers
                )

                for t in transactions.filter(notification_phone_number=number):
                    t.update_after_sms_notification(
                        response_status, message_id
                    )

            return 'SUCCESS'

    except AcceptException as e:
        log_error(e)
        result = e.args[0]
    except requests.RequestException as e:
        message = 'ERROR - ACCEPT (btc transfer request to blockchain): {}'.format(repr(e))
        log_error(message)
        result = message

    transactions.update(state=Transaction.PAID)
    return result
