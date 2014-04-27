from django.contrib import admin
from transaction.models import Pricing, Transaction


class PricingAdmin(admin.ModelAdmin):
    fields = ('id', 'start', 'end', 'markup', 'ghs_usd', )
    readonly_fields = ('id', 'start', )


class TransactionAdmin(admin.ModelAdmin):

    fields = (
        'id', 'email', 'btc_wallet_address', 'notification_phone_number',
        'amount_ghs', 'amount_usd', 'initialized_at',
        'state', 'pricing', 'paid_at', 'processed_at',
        'cancelled_at', 'declined_at', 'penalty_in_usd',
    )
    readonly_fields = (
        'id', 'email', 'btc_wallet_address', 'notification_phone_number',
        'amount_ghs', 'amount_usd', 'initialized_at',
    )
    list_display = ('email', 'btc_wallet_address',
                    'notification_phone_number', )
    list_display_links = ('email', 'btc_wallet_address')

admin.site.register(Pricing, PricingAdmin)
admin.site.register(Transaction, TransactionAdmin)
