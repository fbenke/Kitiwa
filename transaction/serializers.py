from rest_framework import serializers
from transaction.models import Transaction
import re


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'email', 'btc_wallet_address', 'notification_phone_number',
            'amount_ghs', 'amount_usd', 'state', 'initialized_at', 'paid_at',
            'processed_at', 'cancelled_at', 'declined_at', 'penalty_in_usd',
            'pricing', 'processed_exchange_rate', 'amount_btc',
        )
        read_only_fields = (
            'id', 'state', 'initialized_at', 'paid_at', 'processed_at',
            'cancelled_at', 'declined_at', 'penalty_in_usd', 'pricing',
            'processed_exchange_rate', 'amount_btc',
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

    def validate_btc_wallet_address(self, attrs, source):
        """
        27 - 34 alphanumeric, first one is 1 or 3
        """

        if not re.match(r'^[1,3][a-zA-Z0-9]{26,33}$', attrs[source]):
            raise serializers.ValidationError(
                'this is not a valid bitcoin address')
        return attrs


    # TODO: validation of the confirmation phone number
    # TODO: validation of amount in ghs and usd?
