import calendar
import requests
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from kitiwa import settings as s
from kitiwa.utils import log_error


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_bitstamp_rate(request):
    rate = get_bitstamp_exchange_rate()
    if rate is not None:
        return Response({'ask': rate})
    else:
        return Response({'error': 'Unable to retrieve rate'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_bitstamp_exchange_rate():
    try:
        get_rate_call = requests.get(s.BITSTAMP_API_TICKER)
        if get_rate_call.status_code == 200:
            try:
                return get_rate_call.json().get('ask')
            except AttributeError:
                log_error('ERROR - BITSTAMP: Ask rate not present in 200 response')
                return None
        else:
            log_error('ERROR - BITSTAMP: Call returned response code: ' + str(get_rate_call.status_code))
            return None
    except requests.RequestException as e:
        log_error('ERROR - BLOCKCHAIN: Call gave a request exception ' + repr(e))
        return None


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


class BitStampRequest(APIView):
    permission_classes = (IsAdminUser,)
    url = None

    def post(self, request):
        params = self.get_params(request)
        if None in params.values():
            log_error('ERROR - BITSTAMP (' + self.url + '): Missing nonce/signature in params')
            return Response({'error': 'Invalid data received'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            r = requests.post(self.url, data=params)
            if r.status_code == 200:
                return Response(r.json())
            else:
                log_error('ERROR - BITSTAMP: Call returned response code: ' + str(r.status_code))
                return Response(r.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            log_error('ERROR - BITSTAMP: Call gave a request exception ' + repr(e))
            return Response({'error': 'Unable to retrieve balance (request exception)'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_params(self, request):
        nonce = request.POST.get('nonce', None)
        signature = request.POST.get('signature', None)
        return {
            'key': s.BITSTAMP_API_KEY,
            'nonce': nonce,
            'signature': signature
        }


class Balance(BitStampRequest):
    url = s.BITSTAMP_API_BALANCE


class OrderBtc(BitStampRequest):
    url = s.BITSTAMP_API_BUY

    def get_params(self, request):
        params = super(BitStampRequest, self).get_params(request)
        params['amount'] = request.POST.get('btcAmount', None)
        params['price'] = request.POST.get('price', None)
        return params


class CancelOrder(BitStampRequest):
    url = s.BITSTAMP_API_CANCEL_ORDER

    def get_params(self, request):
        params = super(BitStampRequest, self).get_params(request)
        params['id'] = request.POST.get('orderId', None)
        return params


class Withdraw(BitStampRequest):
    url = s.BITSTAMP_API_WITHDRAW_BTC

    def get_params(self, request):
        params = super(BitStampRequest, self).get_params(request)
        params['amount'] = request.POST.get('btcAmount', None)
        # params['address'] = request.POST.get('btcAddress', None)
        return params


class Transactions(BitStampRequest):
    url = s.BITSTAMP_API_TRANSACTIONS

    def get_params(self, request):
        params = super(BitStampRequest, self).get_params(request)
        params['limit'] = request.POST.get('limit', s.BITSTAMP_API_DEFAULT_NUM_TRANSACTIONS)
        return params


class Orders(BitStampRequest):
    url = s.BITSTAMP_API_ORDERS
