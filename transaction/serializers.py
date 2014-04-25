from rest_framework import serializers
from transaction.models import Transaction


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ('email', 'btc_wallet_address', 'notification_phone_number',
                  'amount_ghs', 'amount_usd')

        def validate(self, attrs):
            """
            Check that either email or btc_wallet_address is provided (XOR)
            """
            print(attrs)
            if not (attrs['email'] ^ attrs['btc_wallet_address']):
                raise serializers.ValidationError(
                    'provide either an email or btc wallet address (not both)'
                )
            return attrs
