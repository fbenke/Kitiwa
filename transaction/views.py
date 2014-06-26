from django.db import transaction as dbtransaction
from django.utils.datetime_safe import datetime
from django.utils import timezone

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
from kitiwa.settings import BLOCKCHAIN_API_SENDMANY
from kitiwa.settings import KNOXXI_TOPUP_PERCENTAGE, KNOXXI_TOP_UP_ENABLED
from kitiwa.settings import MPOWER_INVD_ACCOUNT_ALIAS_ERROR_MSG, MPOWER_INVD_TOKEN_ERROR_MSG
from kitiwa.settings import PAGA_MERCHANT_KEY
from kitiwa.settings import MPOWER, PAGA, PAYMENT_CURRENCY, GHS, NGN, PAYMENT_PROVIDERS

from superuser.views.blockchain import get_blockchain_exchange_rate

from transaction.models import Transaction, Pricing
from transaction.api_calls import sendgrid_mail, smsgh, knoxxi
from payment.api_calls import mpower
from transaction import serializers
from transaction import permissions
from transaction import utils
from transaction.utils import AcceptException

from payment.models import MPowerPayment


class TransactionViewSet(viewsets.ModelViewSet):

    paginate_by = 20
    serializer_class = serializers.TransactionSerializer
    permission_classes = (permissions.IsAdminOrPostOnly,)
    throttle_classes = (AnonRateThrottle,)

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

            # additional modifications for mpower payments
            if payment_type == MPOWER:
                mpower_response = MPowerPayment.opr_token_response(transaction_id)
                response.data['mpower_response'] = mpower_response
                if mpower_response['response_code'] == '1001':
                    if mpower_response['response_text'].find(MPOWER_INVD_ACCOUNT_ALIAS_ERROR_MSG) != -1:
                        response.status_code = status.HTTP_400_BAD_REQUEST
                    else:
                        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
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

    def post_save(self, obj, created=False):

        # TODO: is there a better way to do this?
        if obj.payment_type == MPOWER:
            mpower_payment = MPowerPayment()
            mpower_payment.transaction = obj
            success = mpower_payment.opr_token_request(
                obj.notification_phone_number, obj.amount_ghs
            )

            if not success:
                obj.state = Transaction.INVALID
                obj.declined_at = timezone.now()
                obj.save()


class TransactionOprCharge(APIView):

    def put(self, request, format=None):
        try:
            transaction_uuid = request.DATA.get('transaction_uuid')
            transaction = Transaction.objects.get(
                transaction_uuid=transaction_uuid,
                state__in=[Transaction.INIT, Transaction.DECLINED]
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

            response_code, response_text = mpower.opr_charge_action(
                opr_token=transaction.mpower_opr_token,
                confirm_token=serializer.data['mpower_confirm_token']
            )

            transaction = Transaction.objects.get(id=transaction.id)

            transaction.update_after_opr_charge(
                response_code=response_code,
                response_text=response_text
            )

            response = Response()

            payload = {
                'mpower_response_code': response_code,
                'mpower_response_text': response_text,
            }

            if response_code == '00':
                sendgrid_mail.notify_admins_paid()
            elif (response_code == '3001') or\
                 (response_code == '1001' and response_text.find(MPOWER_INVD_TOKEN_ERROR_MSG) != -1):
                response.status_code = status.HTTP_400_BAD_REQUEST
            else:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            response.data = payload

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PricingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PricingSerializer
    permission_classes = (IsAdminUser,)
    queryset = Pricing.objects.filter()

    def pre_save(self, obj):
        Pricing.end_previous_pricing()


class PricingCurrent(RetrieveAPIView):
    serializer_class = serializers.PricingSerializer

    def retrieve(self, request, *args, **kwargs):
        self.object = Pricing.objects.get(end__isnull=True)
        serializer = self.get_serializer(self.object)
        return Response(serializer.data)


class PricingLocal(APIView):
    def get(self, request, format=None):
        try:
            usd_list = request.QUERY_PARAMS.get('amount_usd')
            usd_list = usd_list.split(',')
            payment_type = request.QUERY_PARAMS.get('payment_type')
            if(payment_type) not in PAYMENT_PROVIDERS:
                return Response(
                    {'detail': 'Invalid value for \'payment_type\''},
                    status=status.HTTP_400_BAD_REQUEST
                )
            local_conversions = {}
            for amount_usd in usd_list:
                amount_usd = float(amount_usd)
                if amount_usd != round(amount_usd, 2):
                    return Response(
                        {'detail': '\'amount_usd\' may not have more than 2 decimal places'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                local_conversions[amount_usd] = \
                    Transaction.calculate_local_price(amount_usd, payment_type)
            return Response(local_conversions)
        except (AttributeError, ValueError):
            return Response(
                {'detail': 'Invalid parameters (required: \'amount_usd\', \'payment_type\')'},
                status=status.HTTP_400_BAD_REQUEST
            )


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
                    raise AcceptException({'detail': 'Wrong state', 'id': t.id, 'state': t.state},
                                          status.HTTP_403_FORBIDDEN)

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
                    btc_transfer_request_error = True
                else:
                    transactions.update(state=Transaction.PROCESSED, processed_at=datetime.utcnow())
                    combined_sms_confirm, combined_sms_topup = \
                        utils.consolidate_notification_sms(transactions)

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

                    # top up account
                    if KNOXXI_TOP_UP_ENABLED:
                        for number, amount in combined_sms_topup.iteritems():
                            topup = round(amount * KNOXXI_TOPUP_PERCENTAGE, 2)

                            if topup > 0.20:
                                success = knoxxi.direct_top_up(
                                    mobile_number=number,
                                    amount=topup
                                )
                                if success:
                                    smsgh.send_message_topup(
                                        mobile_number=number,
                                        topup=topup
                                    )
            except requests.RequestException:
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
