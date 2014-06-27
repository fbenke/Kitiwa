from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from payment.api_calls import mpower
from payment.utils import MPowerException

from transaction.models import Transaction

from kitiwa.api_calls import sendgrid_mail
from kitiwa.settings import MPOWER_INVD_TOKEN_ERROR_MSG, MPOWER_RESPONSE_SUCCESS,\
    MPOWER_RESPONSE_INSUFFICIENT_FUNDS, MPOWER_RESPONSE_OTHER_ERROR

import re


@api_view(['POST'])
def opr_charge(request):
    # validate parameters
    try:
        transaction_uuid = request.DATA.get('transaction_uuid')
        mpower_confirm_token = request.DATA.get('mpower_confirm_token')
        if not re.match(r'^[0-9]{4}$', mpower_confirm_token):
            raise ValueError('mpower_confirm_token must be a 4-digit pin')
    except (ValueError, AttributeError):
        raise MPowerException({'detail': 'Invalid Parameters'}, status.HTTP_400_BAD_REQUEST)

    # retrieve and update transaction
    try:
        transaction = Transaction.objects.select_related('mpower_payment').get(
            transaction_uuid=transaction_uuid,
            state__in=[Transaction.INIT, Transaction.DECLINED]
        )
        transaction.mpower_payment.mpower_confirm_token = mpower_confirm_token
        transaction.mpower_payment.save()

    except Transaction.DoesNotExist:
        raise MPowerException({'detail': 'No matching transaction found'}, status.HTTP_400_BAD_REQUEST)

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
