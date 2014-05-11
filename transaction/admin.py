from django.contrib import admin

from transaction.models import Pricing, Transaction


class PricingAdmin(admin.ModelAdmin):
    fields = ('id', 'start', 'end', 'markup', 'ghs_usd', )
    readonly_fields = ('id', 'start', )


class TransactionAdmin(admin.ModelAdmin):

    fields = (
        'id', 'btc_wallet_address', 'notification_phone_number',
        'amount_ghs', 'amount_usd', 'amount_btc', 'initialized_at',
        'state', 'pricing', 'paid_at', 'processed_at', 'cancelled_at',
        'declined_at', 'penalty_in_usd', 'processed_exchange_rate',
        'transaction_uuid', 'reference_number', 'mpower_response_code',
        'mpower_response_text', 'mpower_opr_token', 'mpower_confirm_token',
        'mpower_receipt_url', 'smsgh_response_status', 'smsgh_message_id',
    )

    readonly_fields = (
        'id', 'amount_ghs', 'amount_btc', 'initialized_at', 'processed_exchange_rate',
        'transaction_uuid', 'reference_number', 'mpower_response_code',
        'mpower_response_text', 'mpower_opr_token', 'mpower_confirm_token',
        'mpower_receipt_url', 'smsgh_response_status', 'smsgh_message_id',
    )

    list_display = (
        'btc_wallet_address', 'notification_phone_number', 'state',
        'amount_usd',
    )

    list_display_links = ('btc_wallet_address', )

    list_filter = ('state',)

admin.site.register(Pricing, PricingAdmin)
admin.site.register(Transaction, TransactionAdmin)
