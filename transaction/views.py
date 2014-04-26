from transaction.models import Transaction
from transaction import serializers
from rest_framework import viewsets
from rest_framework.throttling import AnonRateThrottle


class TransactionViewSet(viewsets.ModelViewSet):

    paginate_by = 20
    serializer_class = serializers.TransactionSerializer
    throttle_classes = (AnonRateThrottle,)

    def get_queryset(self):
        queryset = Transaction.objects.all()
        state = self.request.QUERY_PARAMS.get('state', None)
        if state is not None:
            queryset = queryset.filter(state=state)
        return queryset
