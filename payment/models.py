from django.db import models
from django.utils import timezone

from transaction.models import Transaction

from payment.api_calls import mpower


class MPowerPayment(models.Model):

    transaction = models.ForeignKey(
        Transaction,
        related_name='mpower_payments',
        help_text='Transaction associated with this payment'
    )

    mpower_opr_token = models.CharField(
        'MPower OPR Token',
        max_length=30,
        blank=True,
        help_text='OPR Token returned by MPower after initialization of an Onsite Payment Request'
    )

    mpower_confirm_token = models.CharField(
        'MPower Confirmation Token',
        max_length=10,
        blank=True,
        help_text='Token sent to user by MPower via SMS / Email to confirm Onsite Payment Request'
    )

    mpower_invoice_token = models.CharField(
        'MPower OPR Invoice Token',
        max_length=30,
        blank=True,
        help_text='Only stored for tracking record'
    )

    mpower_response_code = models.CharField(
        'MPower Response Code',
        max_length=50,
        blank=True,
        help_text='Only stored for tracking record'
    )

    mpower_response_text = models.CharField(
        'MPower Response Text',
        max_length=200,
        blank=True,
        help_text='Only stored for tracking record'
    )

    def opr_token_request(self, phone_number, amount):
        response_code, response_text, opr_token, invoice_token = (
            mpower.opr_token_request(
                mpower_phone_number=phone_number,
                amount=amount
            )
        )

        self.mpower_response_code = response_code
        self.mpower_response_text = response_text

        success = False

        if response_code == '00':
            self.mpower_opr_token = opr_token
            self.mpower_invoice_token = invoice_token
            success = True

        self.save()

        return success

    @staticmethod
    def opr_token_response(transaction_id):
        mpower_payment = MPowerPayment.objects.get(transaction__id=transaction_id)
        response = {
            'response_code': mpower_payment.mpower_response_code,
            'response_text': mpower_payment.mpower_response_text
        }
        return response

    def update_after_opr_charge(self, response_code, response_text):

        self.mpower_response_code = response_code
        self.mpower_response_text = response_text

        if response_code == '00':
            self.transaction.state = Transaction.PAID
            self.transaction.paid_at = timezone.now()

        else:
            self.transaction.state = Transaction.DECLINED
            self.transaction.declined_at = timezone.now()

        self.save()
