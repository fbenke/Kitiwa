from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from payment.models import PagaPayment
from payment.utils import PagaException

from transaction.models import Transaction

from kitiwa.api_calls import sendgrid_mail
from kitiwa.utils import log_error
from kitiwa.settings import ENV_SITE_MAPPING, ENV, SITE_USER, ENV_LOCAL
from kitiwa.settings import PAGA_MERCHANT_KEY, PAGA_PRIVATE_KEY

from django.utils import timezone
from django.db import transaction as dbtransaction


@api_view(['POST'])
def backend_callback(request):

    try:
        invoice = request.DATA.get('invoice')
        transaction_id = request.DATA.get('transaction_id')
        transaction_reference = request.DATA.get('transaction_reference')

        notification_private_key = request.DATA.get('notification_private_key')
        merchant_key = request.DATA.get('merchant_key')

        amount = float(request.DATA.get('amount'))
        transaction_datetime = request.DATA.get('transaction_datetime')

        # find transaction
        transaction = Transaction.objects.get(transaction_uuid=invoice)
        if transaction.state != Transaction.INIT:
            message = 'ERROR - PAGA: request refers to transaction in state {}'
            message = message.format(transaction.state)
            raise PagaException

        # validate merchant key
        if merchant_key != PAGA_MERCHANT_KEY:
            message = 'ERROR - PAGA: request with invalid merchant key ({})'
            message = message.format(merchant_key)
            raise PagaException

        # validate private key
        if notification_private_key != PAGA_PRIVATE_KEY:
            message = 'ERROR - PAGA: request with invalid private key ({})'
            message = message.format(notification_private_key)
            raise PagaException

        # double check amount
        if amount != transaction.amount_ngn:
            message = 'ERROR - PAGA: amount in request does not match database value (db: {}, paga: {})'
            message = message.format(transaction.amount_ngn, amount)
            raise PagaException

        # create PagaPayment
        paga_payment = PagaPayment(
            transaction=transaction, paga_transaction_reference=transaction_reference,
            paga_transaction_id=transaction_id, processed_at=transaction_datetime)

        # update transaction and paga payment (all-or-nothing)
        with dbtransaction.atomic():
            transaction.state = Transaction.PAID
            transaction.paid_at = timezone.now()
            transaction.save()
            paga_payment.save()

        sendgrid_mail.notify_admins_paid()

        return Response({'detail': 'Success'})

    except Transaction.DoesNotExist as e:
        message = 'ERROR - PAGA: no transaction found for uuid {}, {}'
        log_error(message.format(invoice, e))

    except PagaException as e:
        log_error(message)

    except (KeyError, TypeError) as e:
        message = 'ERROR - PAGA: received invalid payment notification, {}, {}'
        log_error(message.format(request.DATA, e))

    return Response({'detail': 'Error'}, status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def user_callback(request):

    paga_status = request.POST.get('status')
    merchant_key = request.POST.get('key')
    reference_number = request.POST.get('reference_number')
    fee = request.POST.get('fee')
    reference = request.POST.get('reference')
    exchangeRate = request.POST.get('exchange_rate')
    currency = request.POST.get('currency')
    customer_account = request.POST.get('customer_account')
    process_code = request.POST.get('process_code')
    invoice = request.POST.get('invoice')
    test = request.POST.get('test')
    message = request.POST.get('message')
    total = request.POST.get('total')
    transaction_id = request.POST.get('transaction_id')

    kitiwa_reference = request.GET.get('reference', 'error')

    http_prefix = 'https://'
    if ENV == ENV_LOCAL:
        http_prefix = 'http://'

    if paga_status == 'SUCCESS':
        if merchant_key != PAGA_MERCHANT_KEY:
            return redirect(http_prefix + ENV_SITE_MAPPING[ENV][SITE_USER] + '/#!/failed?error=merchantkey')
        else:
            return redirect(http_prefix + ENV_SITE_MAPPING[ENV][SITE_USER] + '/#!/thanks?reference=' + kitiwa_reference +
                            '&pagaTransactionId=' + transaction_id)
    else:
        return redirect(http_prefix + ENV_SITE_MAPPING[ENV][SITE_USER] + '/#!/failed?status=' + status)
