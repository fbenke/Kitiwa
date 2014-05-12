import decimal
import requests
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from kitiwa import settings as s


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def get_balance(request):
    password = request.POST.get('password', None)
    r = requests.get(s.BLOCKCHAIN_API_BALANCE, params={'password': password})

    if r.json().get('balance') is None:
        return Response(r.json(), status=status.HTTP_403_FORBIDDEN)
    else:
        rate = get_blockchain_exchange_rate()
        if rate is not None:
            btc = decimal.Decimal(r.json().get('balance'))/s.ONE_SATOSHI
            usd = btc * decimal.Decimal(rate)
            return Response({'btc': btc, 'usd': '{0:.2f}'.format(usd), 'rate': rate})


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_rate(request):
    rate = get_blockchain_exchange_rate()
    if rate is not None:
        return Response({'rate': rate})
    else:
        return Response({'error': 'Unable to retrieve rate'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_blockchain_exchange_rate():
    try:
        get_rate_call = requests.get(s.BLOCKCHAIN_TICKER)
        if get_rate_call.status_code == 200:
            try:
                return get_rate_call.json().get('USD').get('buy')
            except AttributeError:
                return None
        else:
            return None
    except requests.RequestException:
        return None