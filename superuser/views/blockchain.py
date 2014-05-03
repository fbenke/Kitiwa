import decimal
import requests
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from kitiwa import settings as s
from transaction.utils import get_blockchain_exchange_rate


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
            print btc, usd
            return Response({'btc': btc, 'usd': '{0:.2f}'.format(usd), 'rate': rate})


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_rate(request):
    rate = get_blockchain_exchange_rate()
    if rate is not None:
        return Response({'rate': rate})
    else:
        return Response({'error': 'Unable to retrieve rate'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
