from django.contrib import admin

from transaction.models import Pricing, Transaction


class PricingAdmin(admin.ModelAdmin):
    fields = (
        'id', 'start', 'end', 'markup_cat_1', 'markup_cat_1_upper',
        'markup_cat_2', 'markup_cat_2_upper', 'markup_cat_3',
        'markup_cat_3_upper', 'markup_cat_4', 'ghs_usd', 'ngn_usd',
    )
    readonly_fields = ('id', 'start', )
    list_display = (
        'start', 'end', 'ghs_usd', 'markup_cat_1', 'markup_cat_2',
        'markup_cat_3', 'markup_cat_4'
    )


class TransactionAdmin(admin.ModelAdmin):

    fields = (
        'id', 'btc_wallet_address', 'notification_phone_number', 'payment_type',
        'amount_ghs', 'amount_usd', 'amount_btc', 'amount_ngn', 'initialized_at',
        'state', 'pricing', 'paid_at', 'processed_at', 'cancelled_at',
        'declined_at', 'processed_exchange_rate', 'transaction_uuid',
        'reference_number', 'smsgh_response_status', 'smsgh_message_id',
    )

    readonly_fields = (
        'id', 'amount_ghs', 'amount_btc', 'amount_ngn', 'initialized_at',
        'payment_type', 'processed_exchange_rate', 'transaction_uuid',
        'reference_number', 'smsgh_response_status', 'smsgh_message_id',
    )

    list_display = (
        'btc_wallet_address', 'notification_phone_number', 'state',
        'amount_usd', 'amount_ngn'
    )

    list_display_links = ('btc_wallet_address', )

    list_filter = (
        'state', 'paid_at',
    )

    search_fields = (
        'btc_wallet_address', 'notification_phone_number', 'reference_number',
    )

admin.site.register(Pricing, PricingAdmin)
admin.site.register(Transaction, TransactionAdmin)
