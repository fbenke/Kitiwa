import calendar
import requests
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from kitiwa import settings as s


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_rate(request):
    r = requests.get(s.BITSTAMP_API_TICKER)
    if r.status_code == 200:
        return Response(r.json())
    else:
        return Response(r.json(), status=r.status_code)



@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_request_data(request):
    try:
        return Response(
            {
                'nonce': calendar.timegm(datetime.utcnow().utctimetuple()),
                'clientId': s.BITSTAMP_CLIENT_ID,
                'apiKey': s.BITSTAMP_API_KEY,
                'saltBase64': s.BITSTAMP_ENC_SALT_BASE64,
                'ivBase64': s.BITSTAMP_ENC_IV_BASE64,
                'encApiSecretBase64': s.BITSTAMP_ENC_API_SECRET_BASE64
            }
        )
    except AttributeError:
        return Response({'error': 'Unable to retrieve data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def get_balance(request):
    nonce = request.POST.get('nonce', None)
    signature = request.POST.get('signature', None)
    if nonce is not None and signature is not None:
        params = {
            'key': s.BITSTAMP_API_KEY,
            'nonce': nonce,
            'signature': signature
        }
        r = requests.post(s.BITSTAMP_API_BALANCE, data=params)
        if r.status_code == 200:
            return Response(r.json())
        else:
            return Response(r.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Invalid data received'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)