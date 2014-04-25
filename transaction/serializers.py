from rest_framework import serializers
from transaction.models import Transaction


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ('email', 'btc_wallet_address', 'notification_phone_number',
                  'amount_ghs', 'amount_usd')
