from django.contrib import admin

from payment.models import MPowerPayment, PagaPayment


class MPowerAdmin(admin.ModelAdmin):

    fields = (
        'id', 'mpower_response_code', 'mpower_response_text', 'mpower_opr_token',
        'mpower_confirm_token', 'mpower_invoice_token', 'transaction'
    )

    readonly_fields = fields

    list_display = ('id', )


class PagaAdmin(admin.ModelAdmin):
    fields = (
        'id', 'transaction', 'paga_transaction_reference',
        'paga_transaction_id', 'paga_processed_at', 'status'
    )

    readonly_fields = fields

    list_display = ('id', )

admin.site.register(MPowerPayment, MPowerAdmin)
admin.site.register(PagaPayment, PagaAdmin)
