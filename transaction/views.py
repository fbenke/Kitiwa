from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
import time
from rest_framework.throttling import AnonRateThrottle
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
        time.sleep(3)

        transactions.update(state=Transaction.PROCESSED)
        return Response({'status': 'success'})
    except (Transaction.DoesNotExist, ValueError, AttributeError):
        return Response({'detail': 'Invalid ID'},
                        status=status.HTTP_400_BAD_REQUEST)
