import math

from django.utils.datetime_safe import datetime
import requests
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from kitiwa.settings import BLOCKCHAIN_TICKER, ONE_SATOSHI,\
    BLOCKCHAIN_API_SENDMANY, BLOCKCHAIN_TRANSACTION_FEE_SATOSHI
from transaction.models import Transaction, Pricing
from transaction import serializers
from transaction import permissions
from transaction import mpower_api_calls


class TransactionViewSet(viewsets.ModelViewSet):

    paginate_by = 20
    serializer_class = serializers.TransactionSerializer
    permission_classes = (permissions.IsAdminOrPostOnly,)
    throttle_classes = (AnonRateThrottle,)

    def create(self, request, format=None):
        response = super(viewsets.ModelViewSet, self).create(
            request=request, format=format)
        try:
            response.data = {'mpower_response_code': response.data['mpower_response_code']}
        except KeyError:
            pass
        return response

    def get_queryset(self):
        queryset = Transaction.objects.all()
        state = self.request.QUERY_PARAMS.get('state', None)
        if state is not None:
            queryset = queryset.filter(state=state)
        return queryset

    def pre_save(self, obj):
        obj.calculate_ghs_price()

    def post_save(self, obj, created=False):

        phone_number = obj.notification_phone_number
        amount = obj.amount_ghs

        response_code, response_text, opr_token, invoice_token = (
            mpower_api_calls.opr_token_request(
                mpower_phone_number=phone_number,
                amount=amount
            )
        )

        obj.update_after_opr_token_request(
            response_code=response_code,
            response_text=response_text,
            mpower_opr_token=opr_token,
            mpower_invoice_token=invoice_token)

        obj.save()


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
        for t in transactions:
            btc = int(math.ceil((t.amount_usd / rate) * ONE_SATOSHI))
            t.amount_btc = btc
            t.processed_exchange_rate = rate
            t.save()

        # Combine transactions with same wallet address
        combined_transactions = {}
        for t in transactions:
            try:
                combined_transactions[t.btc_wallet_address] += t.amount_btc
            except KeyError:
                combined_transactions[t.btc_wallet_address] = t.amount_btc

        # Prepare request and send
        recipients = '{'
        for wallet, amount in combined_transactions.items():
            recipients += '"{add}":{amt},'.format(add=wallet, amt=amount)
        # remove last comma and add closing brace
        recipients = recipients[:-1] + '}'

        send_many_error = False
        try:
            r = requests.get(BLOCKCHAIN_API_SENDMANY, params={
                'password': password1,
                'second_password': password2,
                'recipients': recipients,
                'note': 'Buy Bitcoins in Ghana @ http://kitiwa.com ' +
                        'Exchange Rate: {rate}, '.format(rate=rate) +
                        'Source: Blockchain Exchange Rates Feed, ' +
                        'Timestamp: {time} UTC'.format(time=datetime.utcnow())
            })
            if r.json().get('error'):
                print r.json()
                # {"error": "Insufficient Funds Available: 365767 Needed: 1809656"}
                # add up:1799656 needed: 1809656 balance: 10000 satoshi
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
