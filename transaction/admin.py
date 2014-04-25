from django.contrib import admin
from transaction.models import Pricing, Transaction


class PricingAdmin(admin.ModelAdmin):
    fields = ('start', 'end', 'markup', 'ghs_usd', )


class TransactionAdmin(admin.ModelAdmin):
    fields = ('email', 'btc_wallet_address', 'notification_phone_number',
              'amount_ghs', 'amount_usd', 'state', 'pricing')
    readonly_fields = ('initialized_at', 'paid_at', 'processed_at',
                       'cancelled_at', 'declined_at', 'penalty_in_usd',
                       'pricing', )
    list_display = ('email', 'btc_wallet_address',
                    'notification_phone_number', )
    list_display_links = ('email', 'btc_wallet_address')

admin.site.register(Pricing, PricingAdmin)
admin.site.register(Transaction, TransactionAdmin)
