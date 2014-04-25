from transaction.models import Transaction
from transaction.serializers import TransactionSerializer
from rest_framework import generics


class TransactionAPI(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    paginate_by = 20
