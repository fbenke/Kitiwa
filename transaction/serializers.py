from rest_framework import serializers
from transaction.models import Transaction, Pricing
import re


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'email', 'btc_wallet_address', 'notification_phone_number',
            'amount_usd', 'state', 'initialized_at', 'paid_at', 'processed_at',
            'cancelled_at', 'declined_at', 'penalty_in_usd', 'pricing',
            'processed_exchange_rate', 'amount_ghs', 'amount_btc',
            'mpower_token',
        )
        read_only_fields = (
            'id', 'state', 'initialized_at', 'paid_at', 'processed_at',
            'cancelled_at', 'declined_at', 'penalty_in_usd', 'pricing',
            'processed_exchange_rate', 'amount_ghs', 'amount_btc',
            'mpower_token',
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

        if attrs[source] == '':
            return attrs

        if not re.match(r'^[1,3][a-zA-Z0-9]{26,33}$', attrs[source]):
            raise serializers.ValidationError(
                'this is not a valid bitcoin address')

        return attrs

    def validate_notification_phone_number(self, attrs, source):
        # TODO: come up with more advanced phone number validation
        if not re.match(r'^[0-9]{10,15}$', attrs[source]):
            raise serializers.ValidationError(
                'phone number must be 10 - 15 numeric characters')
        return attrs


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = ('markup', 'ghs_usd')

    def validate_markup(self, attrs, source):
        if not (0.0 <= attrs[source] <= 1.0):
            raise serializers.ValidationError(
                'markup has to be a value between 0 and 1')
        return attrs
