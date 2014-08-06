from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from payment.utils import MPowerException

from transaction.models import Transaction

from kitiwa.api_calls import sendgrid_mail
from kitiwa.settings import MPOWER_RESPONSE_SUCCESS, MPOWER_RESPONSE_ACCOUNT_ERROR,\
    MPOWER_RESPONSE_INPUT_ERROR

import re


@api_view(['POST'])
def opr_charge(request):

    try:
        # validate parameters
        transaction_uuid = request.DATA.get('transaction_uuid')
        mpower_confirm_token = request.DATA.get('mpower_confirm_token')

        if not re.match(r'^[0-9]{4}$', mpower_confirm_token):
            raise MPowerException('mpower_confirm_token must be a 4-digit pin')

        # retrieve and update transaction
        transaction = Transaction.objects.select_related('mpower_payment').get(
            transaction_uuid=transaction_uuid,
            state__in=[Transaction.INIT, Transaction.DECLINED]
        )

    except (MPowerException, TypeError):
        return Response({'detail': 'Invalid Parameters'}, status.HTTP_400_BAD_REQUEST)

    except Transaction.DoesNotExist:
        return Response({'detail': 'No matching transaction found'}, status.HTTP_400_BAD_REQUEST)

    response = Response()

    response_code, response_text = transaction.mpower_payment.opr_charge(mpower_confirm_token)

    response.data = {
        'mpower_response_code': response_code,
        'mpower_response_text': response_text,
    }

    if response_code == MPOWER_RESPONSE_SUCCESS:
        # TODO: make this a background task
        sendgrid_mail.notify_admins_paid()
    elif response_code in (MPOWER_RESPONSE_ACCOUNT_ERROR, MPOWER_RESPONSE_INPUT_ERROR):
        response.status_code = status.HTTP_400_BAD_REQUEST
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return response
