from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from payment import serializers
from payment.models import PagaPayment
from payment.api_calls import mpower
from payment.utils import PagaException

from transaction.models import Transaction

from kitiwa.api_calls import sendgrid_mail
from kitiwa.utils import log_error
from kitiwa.settings import MPOWER_INVD_TOKEN_ERROR_MSG, MPOWER_RESPONSE_SUCCESS,\
    MPOWER_RESPONSE_INSUFFICIENT_FUNDS, MPOWER_RESPONSE_OTHER_ERROR
from kitiwa.settings import PAGA_MERCHANT_KEY, PAGA_PRIVATE_KEY

from django.utils import timezone
from django.db import transaction as dbtransaction

import re


class RetrievePayment(RetrieveAPIView):
    serializer_class = serializers.PaymentSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        print pk
        try:
            self.object = Transaction.objects.select_related('mpower_payment').get(id=pk)
        except Transaction.DoesNotExist:
            return Response({'detail': 'Invalid ID'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(self.object.mpower_payment)
        return Response(serializer.data)


@api_view(['POST'])
def mpower_opr_charge(request):

    # validate parameters
    try:
        transaction_uuid = request.DATA.get('transaction_uuid')
        mpower_confirm_token = request.DATA.get('mpower_confirm_token')
        if not re.match(r'^[0-9]{4}$', mpower_confirm_token):
            raise ValueError('mpower_confirm_token must be a 4-digit pin')
    except (ValueError, AttributeError, TypeError):
        return Response({'detail': 'Invalid Parameters'}, status.HTTP_400_BAD_REQUEST)

    # retrieve and update transaction
    try:
        transaction = Transaction.objects.select_related('mpower_payment').get(
            transaction_uuid=transaction_uuid,
            state__in=[Transaction.INIT, Transaction.DECLINED]
        )
        transaction.mpower_payment.mpower_confirm_token = mpower_confirm_token
        transaction.mpower_payment.save()

    except Transaction.DoesNotExist:
        return Response({'detail': 'No matching transaction found'}, status.HTTP_400_BAD_REQUEST)

    response_code, response_text = mpower.opr_charge_action(
        opr_token=transaction.mpower_payment.mpower_opr_token,
        confirm_token=mpower_confirm_token
    )

    transaction.mpower_payment.update_after_opr_charge(
        response_code=response_code,
        response_text=response_text
    )

    response = Response()

    payload = {
        'mpower_response_code': response_code,
        'mpower_response_text': response_text,
    }

    if response_code == MPOWER_RESPONSE_SUCCESS:
        sendgrid_mail.notify_admins_paid()
    elif (response_code == MPOWER_RESPONSE_INSUFFICIENT_FUNDS) or\
         (response_code == MPOWER_RESPONSE_OTHER_ERROR and
          response_text.find(MPOWER_INVD_TOKEN_ERROR_MSG) != -1):
        response.status_code = status.HTTP_400_BAD_REQUEST
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    response.data = payload

    return response


@api_view(['POST'])
def paga_payment_notification(request):

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
