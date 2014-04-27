import math
from django.utils.datetime_safe import datetime
import requests
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
import time
from rest_framework.throttling import AnonRateThrottle
from kitiwa.settings import BLOCKCHAIN_TICKER, ONE_SATOSHI, BLOCKCHAIN_API_SENDMANY
from transaction.models import Transaction
from transaction import serializers
from transaction import permissions


class TransactionViewSet(viewsets.ModelViewSet):

    paginate_by = 20
    serializer_class = serializers.TransactionSerializer
    permission_classes = (permissions.IsAdminOrPostOnly,)
    throttle_classes = (AnonRateThrottle,)

    def get_queryset(self):
        queryset = Transaction.objects.all()
        state = self.request.QUERY_PARAMS.get('state', None)
        if state is not None:
            queryset = queryset.filter(state=state)
        return queryset


class PricingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PricingSerializer
    permission_classes = (IsAdminUser,)

    def pre_save(self, obj):
        obj.end_previous_pricing()


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def accept(request):
    # Expects a comma separated list of ids as a POST param called ids
    try:
        transactions = Transaction.objects.filter(id__in=request.POST.get('ids', None).split(','))
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)

        if not transactions or not password1 or not password2:
            return Response({'detail': 'Invalid IDs and/or Passwords'}, status=status.HTTP_400_BAD_REQUEST)

        # If any transaction is not PAID, fail the whole request
        for t in transactions:
            if t.state != Transaction.PAID:
                return Response({
                                'detail': 'Wrong state',
                                'id': t.id,
                                'state': t.state
                                },
                                status=status.HTTP_403_FORBIDDEN)

        # Make request to blockchain using passwords, if everything succeeds, update transactions
        # https://blockchain.info/merchant/$guid/sendmany?password=$main_password&second_password=$second_password
        # &recipients=$recipients&shared=$shared&fee=$fee
        #
        # $guid = on login page while logging in (hyphen separated string)
        #
        # $recipients = {
        #   "1JzSZFs2DQke2B3S4pBxaNaMzzVZaG4Cqh": 100000000,
        #   "12Cf6nCcRtKERh9cQm3Z29c9MWvQuFSxvT": 1500000000,
        #   "1dice6YgEVBf88erBFra9BHf6ZMoyvG88": 200000000
        # }
        #
        # http://blockchain.info/api/blockchain_wallet_api
        # Not confident about security yet simulate call using sleep

        get_rate = requests.get(BLOCKCHAIN_TICKER)
        rate = None
        get_rate_error = False
        if get_rate.status_code == 200:
            try:
                rate = get_rate.json().get('USD').get('buy')
            except AttributeError:
                get_rate_error = True
        else:
            get_rate_error = True

        if get_rate_error or rate is None:
            return Response({'detail': 'Failed to retrieve exchange rate'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        recipient_list = []
        for t in transactions:
            btc = int(math.ceil((t.amount_usd/rate)*ONE_SATOSHI))
            recipient = (t.btc_wallet_address, btc)
            # t.amount_btc = btc
            # t.save()
            recipient_list.append(recipient)

        recipients = '{'
        for i, r in enumerate(recipient_list):
            recipients += '"{add}":{amt}'.format(add=r[0], amt=r[1])
            if i != (len(recipient_list) - 1):
                recipients += ','
        recipients += '}'

        params = {
            'password': password1,
            'second_password': password2,
            'recipients': recipients,
            'note': 'Buy Bitcoins in Ghana @ http://kitiwa.com ' +
                    '- TEST TRANSACTION. ' +
                    'Exchange Rate: {rate}, '.format(rate=rate) +
                    'Source: Blockchain Exchange Rates Feed, ' +
                    'Timestamp: {time} UTC'.format(time=datetime.utcnow())
        }

        r = requests.get(BLOCKCHAIN_API_SENDMANY, params=params)

        if r.json().get('error'):
            return Response(r.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            transactions.update(state=Transaction.PROCESSED)
            return Response({'status': 'success'})


    except (Transaction.DoesNotExist, ValueError, AttributeError):
        return Response({'detail': 'Invalid ID'},
                        status=status.HTTP_400_BAD_REQUEST)
