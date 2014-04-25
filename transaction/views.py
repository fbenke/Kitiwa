from transaction.models import Transaction
from transaction import serializers
from rest_framework import viewsets


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    paginate_by = 20

    def get_serializer_class(self):
        if self.action == 'update':
            return serializers.UpdateTransactionSerializer
        return serializers.TransactionSerializer
