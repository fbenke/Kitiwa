from django.db import transaction as dbtransaction

from rest_framework import viewsets
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from kitiwa.settings import PAGA_MERCHANT_KEY
from kitiwa.settings import MPOWER, PAGA, PAYMENT_CURRENCY, GHS, NGN, CURRENCIES

from transaction import serializers
from transaction import permissions
from transaction.models import Transaction, Pricing
from transaction.utils import AcceptException, PricingException
from transaction.tasks import add, process_transactions

from payment.models import MPowerPayment


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

    try:
        with dbtransaction.atomic():

            ids = request.DATA.get('ids', None).split(',')

            transactions = Transaction.objects.select_for_update().filter(id__in=ids)

            # Expects a comma separated list of ids as a POST param called ids
            try:
                password1 = request.DATA.get('password1', None)
                password2 = request.DATA.get('password2', None)
            except (ValueError, AttributeError):
                raise AcceptException({'detail': 'Invalid ID'}, status.HTTP_400_BAD_REQUEST)

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

            # Set transactions to PROCESSING
            transactions.update(state=Transaction.PROCESSING)

            result = process_transactions.delay(ids, password1, password2)

            return Response({'task_id': result.id})

    except AcceptException as e:
        return Response(e.args[0], status=e.args[1])
    except Transaction.DoesNotExist:
        return Response({'detail': 'Invalid ID'}, status=status.HTTP_400_BAD_REQUEST)
    except AttributeError:
        return Response({'detail': 'Invalid Input'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_accept_status(request):
    try:
        task_id = request.GET.get('task_id')
        if task_id is None:
            raise AttributeError
        result = process_transactions.AsyncResult(task_id)
        if result.ready():
            response = {'status': result.get()}
        else:
            response = {'status': 'Background Task not finished yet.'}
        return Response(response)
    except AttributeError:
        return Response({'detail': 'Invalid Input'}, status=status.HTTP_400_BAD_REQUEST)


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
    result = add.delay(4, 4)
    return Response({'task_id': result.id})


@api_view(['POST'])
def result(request):
    task_id = request.DATA.get('task_id')
    result = add.AsyncResult(task_id)
    if result.ready():
        response = {'result': result.get()}
    else:
        response = {'result': 'Task not finished yet.'}
    return Response(response)
