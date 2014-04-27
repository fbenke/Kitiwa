import math

from django.utils.datetime_safe import datetime
import requests
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from kitiwa.settings import BLOCKCHAIN_TICKER, ONE_SATOSHI, BLOCKCHAIN_API_SENDMANY
from transaction.models import Transaction, Pricing
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
        Pricing.end_previous_pricing()


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def accept(request):
    # Expects a comma separated list of ids as a POST param called ids
    try:
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        transactions = Transaction.objects.filter(id__in=request.POST.get('ids', None).split(','))

        # VALIDATION
        # Validate Input
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

        # Get latest exchange rate
        get_rate_error = False
        try:
            get_rate = requests.get(BLOCKCHAIN_TICKER)
            rate = None
            if get_rate.status_code == 200:
                try:
                    rate = get_rate.json().get('USD').get('buy')
                except AttributeError:
                    get_rate_error = True
            else:
                get_rate_error = True
        except requests.exceptions.RequestException:
            get_rate_error = True

        if get_rate_error or rate is None:
            return Response({'detail': 'Failed to retrieve exchange rate'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Calculate amounts to send based on latest exchange rate
        recipient_list = []
        for t in transactions:
            btc = int(math.ceil((t.amount_usd/rate)*ONE_SATOSHI))
            recipient = (t.btc_wallet_address, btc)
            t.amount_btc = btc
            t.processed_exchange_rate = rate
            t.save()
            recipient_list.append(recipient)

        # Prepare request and send
        recipients = '{'
        for i, r in enumerate(recipient_list):
            recipients += '"{add}":{amt}'.format(add=r[0], amt=r[1])
            if i != (len(recipient_list) - 1):
                recipients += ','
        recipients += '}'

        send_many_error = False
        try:
            r = requests.get(BLOCKCHAIN_API_SENDMANY, params={
                'password': 'Tjniov7g5#',
                'second_password': 'Mppt348!',
                'recipients': recipients,
                'note': 'Buy Bitcoins in Ghana @ http://kitiwa.com ' +
                        '- TEST TRANSACTION. ' +
                        'Exchange Rate: {rate}, '.format(rate=rate) +
                        'Source: Blockchain Exchange Rates Feed, ' +
                        'Timestamp: {time} UTC'.format(time=datetime.utcnow())
            })
            if r.json().get('error'):
                send_many_error = True
            else:
                transactions.update(state=Transaction.PROCESSED)
                return Response({'status': 'success'})
        except requests.exceptions.RequestException:
            send_many_error = True

        if send_many_error:
            return Response(r.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except (Transaction.DoesNotExist, ValueError, AttributeError):
        return Response({'detail': 'Invalid ID'},
                        status=status.HTTP_400_BAD_REQUEST)
