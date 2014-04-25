from transaction.models import Transaction
from transaction.serializers import TransactionSerializer
from rest_framework import viewsets


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    paginate_by = 20
