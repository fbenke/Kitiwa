from rest_framework import serializers
from payment import models
from transaction.models import Transaction


class MPowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MPowerPayment
        read_only_fields = (
            'mpower_opr_token', 'mpower_invoice_token',
            'mpower_response_code', 'mpower_response_text',
            'mpower_confirm_token',
        )

        fields = read_only_fields


class PagaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PagaPayment
        read_only_fields = (
            'paga_transaction_reference', 'paga_transaction_id', 'processed_at',
        )
        fields = read_only_fields


class PaymentSerializer(serializers.ModelSerializer):
    mpower_payment = MPowerSerializer(many=False)
    paga_payment = PagaSerializer(many=False)

    class Meta:
        model = Transaction
        fields = ('id', 'mpower_payment', 'paga_payment')
