from rest_framework import serializers
from transaction.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'email', 'btc_wallet_address', 'notification_phone_number',
            'amount_ghs', 'amount_usd', 'state', 'initialized_at', 'paid_at',
            'processed_at', 'cancelled_at', 'declined_at', 'penalty_in_usd',
            'pricing'
        )
        read_only_fields = (
            'id', 'state', 'initialized_at', 'paid_at', 'processed_at',
            'cancelled_at', 'declined_at', 'penalty_in_usd', 'pricing',
        )

    def validate(self, attrs):
        """
        Check that either email or btc_wallet_address is provided (XOR)
        """

        if not ((attrs['email'] == '') ^ (attrs['btc_wallet_address'] == '')):
            raise serializers.ValidationError(
                'provide either an email or btc wallet address (not both)'
            )
        return attrs
