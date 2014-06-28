from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from payment.api_calls import mpower

from transaction.models import Transaction

from payment import serializers
from kitiwa.api_calls import sendgrid_mail
from kitiwa.settings import MPOWER_INVD_TOKEN_ERROR_MSG, MPOWER_RESPONSE_SUCCESS,\
    MPOWER_RESPONSE_INSUFFICIENT_FUNDS, MPOWER_RESPONSE_OTHER_ERROR, ENV_SITE_MAPPING, ENV, SITE_USER, PAGA_MERCHANT_KEY

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
def opr_charge(request):

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


@csrf_exempt
def paga_user_callback(request):

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

    if paga_status == 'SUCCESS':
        if merchant_key != PAGA_MERCHANT_KEY:
            return redirect(ENV_SITE_MAPPING[ENV][SITE_USER] + 'failed?error=merchantkey')
        else:
            return redirect(ENV_SITE_MAPPING[ENV][SITE_USER] + 'thanks?reference=' + kitiwa_reference +
                            '&pagaTransactionId=' + transaction_id)
    else:
        return redirect(ENV_SITE_MAPPING[ENV][SITE_USER] + 'failed?status=' + status)
