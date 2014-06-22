import re

from rest_framework import serializers

from transaction.models import Transaction, Pricing
from transaction.utils import is_valid_btc_address

from kitiwa.settings import MAXIMUM_AMOUNT_BTC_BUYING


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'btc_wallet_address', 'notification_phone_number',
            'amount_usd', 'state', 'initialized_at', 'paid_at', 'processed_at',
            'cancelled_at', 'declined_at', 'penalty_in_usd', 'pricing',
            'processed_exchange_rate', 'amount_ghs', 'amount_btc',
            'mpower_opr_token', 'transaction_uuid', 'reference_number',
            'mpower_invoice_token', 'mpower_response_code',
            'mpower_response_text', 'mpower_confirm_token',
            'smsgh_response_status', 'smsgh_message_id',
        )
        read_only_fields = (
            'id', 'state', 'initialized_at', 'paid_at', 'processed_at',
            'cancelled_at', 'declined_at', 'penalty_in_usd', 'pricing',
            'processed_exchange_rate', 'amount_ghs', 'amount_btc',
            'mpower_opr_token', 'transaction_uuid', 'reference_number',
            'mpower_invoice_token', 'mpower_response_code',
            'mpower_response_text', 'mpower_confirm_token',
            'smsgh_response_status', 'smsgh_message_id',
        )

    def validate_btc_wallet_address(self, attrs, source):
        """
        27 - 34 alphanumeric, first one is 1 or 3
        """

        if not is_valid_btc_address(attrs[source]):
            raise serializers.ValidationError(
                'this is not a valid bitcoin address')

        return attrs

    def validate_notification_phone_number(self, attrs, source):
        if not re.match(r'^[0-9]{10,15}$', attrs[source]):
            raise serializers.ValidationError(
                'phone number must be 10 - 15 numeric characters')
        return attrs

    def validate_amount_usd(self, attrs, source):
        if attrs[source] < 1 or attrs[source] > MAXIMUM_AMOUNT_BTC_BUYING:
            raise serializers.ValidationError(
                'amount must be between 1 and {} USD'.format(MAXIMUM_AMOUNT_BTC_BUYING)
            )
        if round(attrs[source], 2) != attrs[source]:
            raise serializers.ValidationError(
                'amount may not have more than two decimal places'
            )
        return attrs


class TransactionOprChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('transaction_uuid', 'mpower_confirm_token',)

    def validate_mpower_confirm_token(self, attrs, source):
        if not re.match(r'^[0-9]{4}$', attrs[source]):
            raise serializers.ValidationError(
                'must be a 4-digit pin'
            )
        return attrs


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = ('markup_cat_1', 'markup_cat_1_upper', 'markup_cat_2',
                  'markup_cat_2_upper', 'markup_cat_3', 'markup_cat_3_upper',
                  'markup_cat_4', 'ghs_usd', 'start', 'end',)
        read_only_fields = ('start', 'end',)

    def validate(self, attrs):
        if not(
                attrs['markup_cat_1_upper'] < attrs['markup_cat_2_upper']
                < attrs['markup_cat_3_upper']
        ):
            raise serializers.ValidationError(
                'each upper bound must be greater than the previous one')
        return attrs

    def validate_markup_cat_1(self, attrs, source):
        return self._validate_markup(attrs, source)

    def validate_markup_cat_2(self, attrs, source):
        return self._validate_markup(attrs, source)

    def validate_markup_cat_3(self, attrs, source):
        return self._validate_markup(attrs, source)

    def validate_markup_cat_4(self, attrs, source):
        return self._validate_markup(attrs, source)

    def _validate_markup(self, attrs, source):
        if not (0.0 <= attrs[source] <= 1.0):
            raise serializers.ValidationError(
                'markup has to be a value between 0 and 1')
        return attrs
