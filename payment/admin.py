from django.contrib import admin

from payment.models import MPower_Payment


class MPowerAdmin(admin.ModelAdmin):

    fields = (
        'mpower_response_code', 'mpower_response_text',
        'mpower_opr_token', 'mpower_confirm_token',
    )

    readonly_fields = (
        'mpower_response_code', 'mpower_response_text',
        'mpower_opr_token', 'mpower_confirm_token',
    )

    list_display = (
        'id', 'transaction',
    )

admin.site.register(MPower_Payment, MPowerAdmin)
