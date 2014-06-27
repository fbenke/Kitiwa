from django.contrib import admin

from transaction.models import Pricing, Transaction


class PricingAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id', 'start', 'end', 'markup_cat_1', 'markup_cat_1_upper',
        'markup_cat_2', 'markup_cat_2_upper', 'markup_cat_3',
        'markup_cat_3_upper', 'markup_cat_4',
    )

    fields = readonly_fields + ('ghs_usd', 'ngn_usd', )

    list_display = (
        'start', 'end', 'ghs_usd', 'ngn_usd', 'markup_cat_1', 'markup_cat_2',
        'markup_cat_3', 'markup_cat_4',
    )


class TransactionAdmin(admin.ModelAdmin):

    readonly_fields = (
        'id', 'btc_wallet_address', 
        'state', 'pricing', 'amount_usd', 'amount_ghs', 'amount_btc',
        'amount_ngn', 'payment_type', 'processed_exchange_rate',
        'transaction_uuid', 'reference_number', 'smsgh_response_status',
        'smsgh_message_id', 'initialized_at', 'paid_at', 'processed_at',
        'cancelled_at', 'declined_at'
    )

    read_and_write_fields = ('notification_phone_number',)

    fields = readonly_fields + read_and_write_fields

    list_display = (
        'initialized_at', 'btc_wallet_address', 'notification_phone_number',
        'state', 'amount_usd',
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
