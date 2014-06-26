from django.contrib import admin

from payment.models import MPowerPayment


class MPowerAdmin(admin.ModelAdmin):

    fields = (
        'mpower_response_code', 'mpower_response_text', 'mpower_opr_token',
        'mpower_confirm_token', 'mpower_invoice_token', 'transaction'
    )

    # readonly_fields = fields

    list_display = ('id', )

admin.site.register(MPowerPayment, MPowerAdmin)
