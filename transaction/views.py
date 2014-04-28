import math

from django.utils.datetime_safe import datetime
import requests
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from kitiwa.settings import ONE_SATOSHI, BLOCKCHAIN_API_SENDMANY, BITCOIN_NOTE
from transaction.models import Transaction, Pricing
from transaction import serializers
from transaction import permissions
from transaction.utils import get_blockchain_exchange_rate


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
    except (Transaction.DoesNotExist, ValueError, AttributeError):
        return Response({'detail': 'Invalid ID'}, status=status.HTTP_400_BAD_REQUEST)

    # VALIDATION
    # Validate Input
    if not transactions or not password1 or not password2:
        return Response({'detail': 'Invalid IDs and/or Passwords'}, status=status.HTTP_400_BAD_REQUEST)

    # If any transaction is not PAID, fail the whole request
    for t in transactions:
        if t.state != Transaction.PAID:
            return Response({'detail': 'Wrong state', 'id': t.id, 'state': t.state},
                            status=status.HTTP_403_FORBIDDEN)

    # USD-BTC CONVERSION
    # Get latest exchange rate
    rate = get_blockchain_exchange_rate()
    if rate is None:
        return Response({'detail': 'Failed to retrieve exchange rate'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Calculate amounts to send based on latest exchange rate
    update_transactions_btc(transactions, rate)

    # Combine transactions with same wallet address
    combined_transactions = consolidate_transactions(transactions)

    # REQUEST
    # Prepare request and send
    recipients = create_recipients_string(combined_transactions)

    request_error = False
    r = None
    try:
        r = requests.get(BLOCKCHAIN_API_SENDMANY, params={
            'password': password1,
            'second_password': password2,
            'recipients': recipients,
            'note': BITCOIN_NOTE.format(rate=rate, time=datetime.utcnow())
        })
        if r.json().get('error'):
            request_error = True
        else:
            transactions.update(state=Transaction.PROCESSED)
            return Response({'status': 'success'})
    except requests.RequestException:
        request_error = True

    if request_error:
        if r:
            return Response(r.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("{'error': 'Error making btc transfer request to blockchain'}",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def update_transactions_btc(transactions, rate):
    for t in transactions:
        btc = int(math.ceil((t.amount_usd/rate)*ONE_SATOSHI))
        t.amount_btc = btc
        t.processed_exchange_rate = rate
        t.save()


def consolidate_transactions(transactions):
    combined_transactions = {}
    for t in transactions:
        try:
            combined_transactions[t.btc_wallet_address] += t.amount_btc
        except KeyError:
            combined_transactions[t.btc_wallet_address] = t.amount_btc
    return combined_transactions


def create_recipients_string(combined_transactions):
    recipients = '{'
    for wallet, amount in combined_transactions.items():
        recipients += '"{add}":{amt},'.format(add=wallet, amt=amount)
    return recipients[:-1] + '}'
