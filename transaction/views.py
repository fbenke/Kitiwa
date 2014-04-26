from transaction.models import Transaction
from transaction import serializers
from rest_framework import viewsets


class TransactionViewSet(viewsets.ModelViewSet):

    paginate_by = 20
    serializer_class = serializers.TransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.all()
        state = self.request.QUERY_PARAMS.get('state', None)
        if state is not None:
            queryset = queryset.filter(state=state)
        return queryset
