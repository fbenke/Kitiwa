from django.utils.datetime_safe import datetime
import requests
from rest_framework import viewsets
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from kitiwa.settings import BITCOIN_NOTE
from transaction import utils
from kitiwa.settings import BLOCKCHAIN_API_SENDMANY
from transaction.models import Transaction, Pricing
from transaction import serializers
from transaction import permissions
from transaction import mpower_api_calls


class TransactionViewSet(viewsets.ModelViewSet):

    paginate_by = 20
    serializer_class = serializers.TransactionSerializer
    permission_classes = (permissions.IsAdminOrPostOnly,)
    throttle_classes = (AnonRateThrottle,)

    def create(self, request, *args, **kwargs):
        response = super(viewsets.ModelViewSet, self).create(
            request=request, format=format)
        try:
            response.data = {
                'mpower_response_code': response.data['mpower_response_code']
            }
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
    queryset = Pricing.objects.filter()

    def pre_save(self, obj):
        Pricing.end_previous_pricing()


class PricingCurrent(RetrieveAPIView):
    serializer_class = serializers.PricingSerializer
    permission_classes = (IsAdminUser,)

    def retrieve(self, request, *args, **kwargs):
        self.object = Pricing.objects.get(end__isnull=True)
        serializer = self.get_serializer(self.object)
        return Response(serializer.data)


class TransactionOprCharge(APIView):

    def put(self, request, format=None):
        try:
            transaction_uid = request.DATA.get('transaction_uid')
            transaction = Transaction.objects.get(
                transaction_uid=transaction_uid, state=Transaction.INIT
            )
            serializer = serializers.TransactionOprChargeSerializer(
                transaction, data=request.DATA
            )
        except Transaction.DoesNotExist:
            return Response(
                {'detail': 'No matching transaction found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    rate = utils.get_blockchain_exchange_rate()
    if rate is None:
        return Response({'detail': 'Failed to retrieve exchange rate'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Update amount_btc based on latest exchange rate
    for t in transactions:
        t.update_btc(rate)

    # Combine transactions with same wallet address
    combined_transactions = consolidate_transactions(transactions)

    # REQUEST
    # Prepare request and send
    recipients = utils.create_recipients_string(combined_transactions)

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
            transactions.update(state=Transaction.PROCESSED, processed_at=datetime.utcnow())
            return Response({'status': 'success'})
    except requests.RequestException:
        request_error = True

    if request_error:
        if r:
            return Response(r.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("{'error': 'Error making btc transfer request to blockchain'}",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Helper method
def consolidate_transactions(transactions):
    combined_transactions = {}
    for t in transactions:
        try:
            combined_transactions[t.btc_wallet_address] += t.amount_btc
        except KeyError:
            combined_transactions[t.btc_wallet_address] = t.amount_btc
    return combined_transactions
