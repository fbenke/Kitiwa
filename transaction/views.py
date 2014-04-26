from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from transaction.models import Transaction
from transaction import serializers
from rest_framework import viewsets
from rest_framework import status


# TODO: Enable IsAdminUser permission on GET all transactions and Update transaction
class TransactionViewSet(viewsets.ModelViewSet):

    paginate_by = 20

    def get_serializer_class(self):
        if self.action == 'update':
            return serializers.UpdateTransactionSerializer
        return serializers.TransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.all()
        state = self.request.QUERY_PARAMS.get('state', None)
        if state is not None:
            queryset = queryset.filter(state=state)
        return queryset


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def accept(request):
    # Expects a comma separated list of ids as a POST param called ids
    try:
        transactions = Transaction.objects.filter(id__in=request.POST.get('ids', None).split(','))
        if not transactions:
            return Response({'detail': 'Invalid ID'}, status=status.HTTP_400_BAD_REQUEST)

        # If any transaction is not PAID, fail the whole request
        for t in transactions:
            if t.state != Transaction.PAID:
                return Response({
                                'detail': 'Wrong state',
                                'id': t.id,
                                'state': t.state
                                },
                                status=status.HTTP_403_FORBIDDEN)
        # If all transactions are good, carry out the change
        transactions.update(state=Transaction.PROCESSED)
        return Response({'status': 'success'})
    except (Transaction.DoesNotExist, ValueError, AttributeError):
        return Response({'detail': 'Invalid ID'}, status=status.HTTP_400_BAD_REQUEST)