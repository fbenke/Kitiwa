import re

from rest_framework import serializers

from transaction.models import Transaction, Pricing
from transaction.utils import is_valid_btc_address

from kitiwa.settings import MAXIMUM_AMOUNT_BTC_BUYING, PAYMENT_PROVIDERS,\
    DIAL_CODES, PAYMENT_DIAL_CODE


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction

        read_and_write_fields = (
            'btc_wallet_address', 'notification_phone_number', 'payment_type',
            'amount_usd',
        )

        read_only_fields = (
            'id', 'state', 'initialized_at', 'paid_at', 'processed_at',
            'cancelled_at', 'declined_at', 'pricing', 'processed_exchange_rate',
            'amount_ghs', 'amount_btc', 'amount_ngn', 'transaction_uuid',
            'reference_number', 'smsgh_response_status', 'smsgh_message_id',
        )

        fields = read_only_fields + read_and_write_fields

    def validate_btc_wallet_address(self, attrs, source):
        """
        27 - 34 alphanumeric, first one is 1 or 3
        """

        if not is_valid_btc_address(attrs[source]):
            raise serializers.ValidationError(
                'this is not a valid bitcoin address'
            )

        return attrs

    def validate_notification_phone_number(self, attrs, source):
        if not re.match(r'^\+[0-9]{12,17}$', attrs[source]):
            raise serializers.ValidationError('invalid format')
        if attrs[source][0:4] not in DIAL_CODES:
            raise serializers.ValidationError('invalid dialing code')
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

    def validate_payment_type(self, attrs, source):
        if attrs[source] not in PAYMENT_PROVIDERS:
            raise serializers.ValidationError(
                'unknown payment provider'
            )
        return attrs

    def validate(self, attrs):
        if (PAYMENT_DIAL_CODE[attrs['payment_type']] !=
                attrs['notification_phone_number'][0:4]):
            raise serializers.ValidationError(
                'dial code and payment type mismatch'
            )
        return attrs


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing

        read_and_write_fields = (
            'markup_cat_1', 'markup_cat_1_upper', 'markup_cat_2',
            'markup_cat_2_upper', 'markup_cat_3', 'markup_cat_3_upper',
            'markup_cat_4', 'ghs_usd', 'ngn_usd'
        )

        read_only_fields = ('start', 'end',)

        fields = read_and_write_fields + read_only_fields

    def validate(self, attrs):
        if not(
                attrs['markup_cat_1_upper'] < attrs['markup_cat_2_upper']
                < attrs['markup_cat_3_upper']
        ):
            raise serializers.ValidationError(
                'each upper bound must be greater than the previous one'
            )
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
