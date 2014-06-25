from django.db import models
from uuid import uuid4
from transaction.models import Transaction
from django.utils import timezone


class MPower_Payment(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        related_name='mpower_payments',
        help_text='Transaction associated with this payment'
    )

    # mpower specific fields
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

    def update_after_opr_token_request(
            self, response_code, response_text,
            mpower_opr_token, mpower_invoice_token):

        self.mpower_response_code = response_code
        self.mpower_response_text = response_text

        if response_code == '00':
            self.mpower_opr_token = mpower_opr_token
            self.mpower_invoice_token = mpower_invoice_token
            self.transaction.transaction_uuid = uuid4()
        else:
            self.transaction.state = Transaction.INVALID
            self.transaction.declined_at = timezone.now()
        self.save()

    def update_after_opr_charge(self, response_code, response_text):

        self.mpower_response_code = response_code
        self.mpower_response_text = response_text

        if response_code == '00':
            self.transaction.state = Transaction.PAID
            self.transaction.paid_at = timezone.now()

        else:
            self.transaction.state = Transaction.DECLINED
            self.transaction.declined_at = timezone.now()

        # TODO: save? what is saved?
        self.save()
