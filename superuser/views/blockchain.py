import decimal
import requests
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from kitiwa import settings as s
from kitiwa.utils import log_error


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def get_balance(request):
    password = request.POST.get('password', None)

    if password is None:
        return Response({'error': 'Password required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        r = requests.get(s.BLOCKCHAIN_API_BALANCE, params={'password': password})
        if r.status_code == 200:
            try:
                btc = decimal.Decimal(r.json().get('balance')) / s.ONE_SATOSHI
            except AttributeError:
                log_error(
                    'ERROR - BLOCKCHAIN (get_balance): "balance" not present in 200 response'
                )
                return Response(r.json(), status=status.HTTP_403_FORBIDDEN)

            rate = get_blockchain_exchange_rate()
            if rate is not None:
                usd = btc * decimal.Decimal(rate)
                return Response({'btc': btc, 'usd': '{0:.2f}'.format(usd), 'rate': rate})
            else:
                return Response({'btc': btc, 'usd': 'Unable to retrieve rate', 'rate': 'Unable to retrieve rate'})
        else:
            log_error(
                'ERROR - BLOCKCHAIN (get_balance): Call returned response code: ' +
                str(r.status_code)
            )
            return Response({'error': 'Unable to retrieve balance (non-200 response)'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.RequestException as e:
        log_error(
            'ERROR - BLOCKCHAIN (get_balance): Call gave a request exception ' +
            repr(e)
        )
        return Response({'error': 'Unable to retrieve balance (request exception)'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_blockchain_exchange_rate():
    try:
        get_rate_call = requests.get(s.BLOCKCHAIN_TICKER)
        if get_rate_call.status_code == 200:
            try:
                return get_rate_call.json().get('USD').get('buy')
            except AttributeError:
                log_error(
                    'ERROR - BLOCKCHAIN (get_blockchain_exchange_rate): USD[buy] not present in 200 response'
                )
                return None
        else:
            log_error(
                'ERROR - BLOCKCHAIN (get_blockchain_exchange_rate): Call returned response code: ' +
                str(get_rate_call.status_code)
            )
            return None
    except requests.RequestException as e:
        log_error(
            'ERROR - BLOCKCHAIN (get_blockchain_exchange_rate): Call gave a request exception ' +
            repr(e)
        )
        return None


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_blockchain_rate(request):
    rate = get_blockchain_exchange_rate()
    if rate is not None:
        return Response({'rate': rate})
    else:
        return Response({'error': 'Unable to retrieve rate'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)