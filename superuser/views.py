import decimal
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import parsers
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from kitiwa import settings as s
from transaction.utils import get_blockchain_exchange_rate


class ObtainStaffAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    model = Token

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            authenticated_user = serializer.object['user']
            token, created = Token.objects.get_or_create(user=authenticated_user)
            if authenticated_user.is_staff:
                return Response({'token': token.key, 'username': authenticated_user.username})
            else:
                return Response({'detail': 'Only staff users can access this login'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_logout(request):
    if request.auth is not None:
        request.auth.delete()
    return Response({'status': 'success'})


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def get_blockchain_balance(request):
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
def get_blockchain_rate(request):
    rate = get_blockchain_exchange_rate()
    if rate is not None:
        return Response({'rate': rate})
    else:
        return Response({'error': 'Unable to retrieve rate'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_bitstamp_rate(request):
    r = requests.get(s.BITSTAMP_API_TICKER)
    if r.status_code == 200:
        return Response(r.json())
    else:
        return Response(r.json(), status=r.status_code)


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_openexchangerate_usd_ghs(request):
    r = requests.get(s.OPEN_EXCHANGE_RATE_API_URL)
    if r.status_code == 200:
        rate = r.json().get('rates').get('GHS')
        return Response({'rate': rate})
    else:
        return Response(r.json(), status=r.status_code)


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_encrypted_data(request):
    try:
        return Response(
            {
                'saltBase64': s.BITSTAMP_ENC_SALT_BASE64,
                'ivBase64': s.BITSTAMP_ENC_IV_BASE64,
                'encApiSecretBase64': s.BITSTAMP_ENC_API_SECRET_BASE64
            }
        )
    except AttributeError:
        return Response({'error': 'Unable to retrieve data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
