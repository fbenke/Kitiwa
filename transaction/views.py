from django.db import transaction as dbtransaction
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

from superuser.views.blockchain import get_blockchain_exchange_rate

from transaction.models import Transaction, Pricing
from transaction.api_calls import smsgh

from transaction import serializers
from transaction import permissions
from transaction import utils
from transaction.utils import AcceptException, PricingException

from payment.models import MPowerPayment

from kitiwa.settings import BITCOIN_NOTE
from kitiwa.settings import BLOCKCHAIN_API_SENDMANY
from kitiwa.settings import PAGA_MERCHANT_KEY
from kitiwa.settings import MPOWER, PAGA, PAYMENT_CURRENCY, GHS, NGN, CURRENCIES

from kitiwa.utils import log_error

from payment.api_calls import mpower


class TransactionViewSet(viewsets.ModelViewSet):

    paginate_by = 20
    serializer_class = serializers.TransactionSerializer
    permission_classes = (permissions.IsAdminOrPostOnly,)
    throttle_classes = (AnonRateThrottle,)

    def post_save(self, obj, created=False):

        # initialize opr token request
        if obj.payment_type == MPOWER:
            mpower_payment = MPowerPayment()
            mpower_payment.transaction = obj
            mpower_payment.opr_token_request(
                obj.notification_phone_number, obj.amount_ghs
            )

    def create(self, request, *args, **kwargs):
        response = super(viewsets.ModelViewSet, self).create(
            request=request, format=format)

        # create a custom response to the frontend
        try:
            payment_type = response.data['payment_type']
            transaction_id = response.data['id']
            amount_ghs = response.data['amount_ghs']
            amount_ngn = response.data['amount_ngn']

            response.data = {
                'reference_number': response.data['reference_number'],
                'transaction_uuid': response.data['transaction_uuid'],
            }

            # add amount in local currency
            if PAYMENT_CURRENCY[payment_type] == GHS:
                response.data['amount_ghs'] = amount_ghs
            elif PAYMENT_CURRENCY[payment_type] == NGN:
                response.data['amount_ngn'] = amount_ngn

            # payment-provider specific information
            if payment_type == MPOWER:
                mpower_response, http_status_code = MPowerPayment.opr_token_response(transaction_id)
                response.data['mpower_response'] = mpower_response
                response.status_code = http_status_code
            elif payment_type == PAGA:
                response.data['merchant_key'] = PAGA_MERCHANT_KEY

        except KeyError:
            response.status_code = status.HTTP_400_BAD_REQUEST

        return response

    def get_queryset(self):
        queryset = Transaction.objects.all()
        state = self.request.QUERY_PARAMS.get('state', None)
        if state is not None:
            queryset = queryset.filter(state=state)
        return queryset


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def accept(request):

    btc_transfer_request = None
    btc_transfer_request_error = False

    try:
        with dbtransaction.atomic():
            transactions = Transaction.objects.select_for_update()\
                .filter(id__in=request.POST.get('ids', None).split(','))

            # Expects a comma separated list of ids as a POST param called ids
            try:
                password1 = request.POST.get('password1', None)
                password2 = request.POST.get('password2', None)
            except (ValueError, AttributeError):
                raise AcceptException({'detail': 'Invalid ID'}, status.HTTP_400_BAD_REQUEST)

            # VALIDATION
            # Validate Input
            if not transactions or not password1 or not password2:
                raise AcceptException({'detail': 'Invalid IDs and/or Passwords'}, status.HTTP_400_BAD_REQUEST)

            # If any transaction is not PAID, fail the whole request
            for t in transactions:
                if t.state != Transaction.PAID:
                    raise AcceptException(
                        {'detail': 'Wrong state', 'id': t.id, 'state': t.state},
                        status.HTTP_403_FORBIDDEN
                    )

            # Verify payment with payment provider
            for t in transactions:
                if not t.verify_payment():
                    log_error('ERROR - ACCEPT: Transaction {} could not be verified as paid'.format(t.id))
                    raise AcceptException(
                        {'detail': 'One of the transactions could not be verified as paid',
                         'id': t.id}, status.HTTP_403_FORBIDDEN
                    )

            # Make sure that there are enough credits in smsgh account to send out confirmation sms
            smsgh_balance = smsgh.check_balance()

            if smsgh_balance is not None:
                if smsgh_balance < len(transactions):
                    raise AcceptException({'detail': 'Not enough credit on SMSGH account'},
                                          status.HTTP_500_INTERNAL_SERVER_ERROR)

            # USD-BTC CONVERSION
            # Get latest exchange rate
            rate = get_blockchain_exchange_rate()
            if rate is None:
                raise AcceptException({'detail': 'Failed to retrieve exchange rate'},
                                      status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Update amount_btc based on latest exchange rate
            for t in transactions:
                t.update_btc(rate)

            # Combine transactions with same wallet address
            combined_transactions = utils.consolidate_transactions(transactions)

            # REQUEST
            # Prepare request and send
            recipients = utils.create_recipients_string(combined_transactions)

            try:
                btc_transfer_request = requests.get(BLOCKCHAIN_API_SENDMANY, params={
                    'password': password1,
                    'second_password': password2,
                    'recipients': recipients,
                    'note': BITCOIN_NOTE
                })
                if btc_transfer_request.json().get('error'):
                    log_error('ERROR - ACCEPT: {}'.format(btc_transfer_request.json()))
                    btc_transfer_request_error = True     
                else:
                    transactions.update(state=Transaction.PROCESSED, processed_at=datetime.utcnow())

                    combined_sms_confirm = utils.consolidate_notification_sms(transactions)

                    # send out confirmation SMS
                    for number, reference_numbers in combined_sms_confirm.iteritems():
                        response_status, message_id = smsgh.send_message_confirm(
                            mobile_number=number,
                            reference_numbers=reference_numbers
                        )

                        for t in transactions.filter(notification_phone_number=number):
                            t.update_after_sms_notification(
                                response_status, message_id
                            )
            except requests.RequestException as e:
                log_error('ERROR - ACCEPT: {}'.format(e))
                btc_transfer_request_error = True
    except AcceptException as e:
        return Response(e.args[0], status=e.args[1])
    except Transaction.DoesNotExist:
        return Response({'detail': 'Invalid ID'}, status=status.HTTP_400_BAD_REQUEST)

    if btc_transfer_request_error:
        if btc_transfer_request:
            return Response(btc_transfer_request.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("{'error': 'Error making btc transfer request to blockchain'}",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'status': 'success'})


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


class PricingLocal(APIView):
    def get(self, request, format=None):
        try:
            usd_list = request.QUERY_PARAMS.get('amount_usd')
            usd_list = usd_list.split(',')
            currency_list = request.QUERY_PARAMS.get('currency')
            currency_list = currency_list.split(',')

            local_conversions = {}
            for currency in currency_list:
                if(currency) not in CURRENCIES:
                    raise PricingException
                conversion = {}
                for amount_usd in usd_list:
                    amount_usd = float(amount_usd)
                    if amount_usd != round(amount_usd, 2):
                        raise PricingException

                    conversion[amount_usd] = \
                        Transaction.calculate_local_price(amount_usd, currency)
                local_conversions[currency] = conversion
            return Response(local_conversions)
        except (AttributeError, ValueError, PricingException):
            return Response(
                {'detail': 'Invalid parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
def test(request):
    mpower.check_invoice_status('test_6f7c6b7396')
    return Response()