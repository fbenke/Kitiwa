from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status

from payment import serializers

from transaction.models import Transaction


class RetrievePayment(RetrieveAPIView):
    serializer_class = serializers.PaymentSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        print pk
        try:
            self.object = Transaction.objects.select_related('mpower_payment').get(id=pk)
        except Transaction.DoesNotExist:
            return Response({'detail': 'Invalid ID'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(self.object)
        return Response(serializer.data)
