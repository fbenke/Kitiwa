from rest_framework import serializers
from payment import models


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MPowerPayment
        read_only_fields = (
            'transaction', 'mpower_opr_token', 'mpower_invoice_token',
            'mpower_response_code', 'mpower_response_text',
            'mpower_confirm_token',
        )

        fields = read_only_fields
