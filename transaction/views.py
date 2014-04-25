from transaction.models import Transaction
from transaction.serializers import TransactionSerializer
from rest_framework import generics


class TransactionInitialization(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
