from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
import math
import random
from uuid import uuid4
from kitiwa.settings import ONE_SATOSHI
from transaction.utils import is_valid_btc_address


class Pricing(models.Model):

    start = models.DateTimeField(
        'Start Time',
        auto_now_add=True,
        help_text='Time at which pricing structure came into effect'
    )
    end = models.DateTimeField(
        'End Time',
        blank=True,
        null=True,
        help_text='Time at which pricing ended. If null, it represents the current pricing structure. ' +
                  'Only one row in this table can have a null value for this column.'
    )

    markup_cat_1 = models.FloatField(
        'Markup Segment 1',
        help_text='Percentage to be added over exchange rate for markup segment 1. Value between 0 and 1.'
    )

    markup_cat_2 = models.FloatField(
        'Markup Segment 2',
        help_text='Percentage to be added over exchange rate for markup segment 2. Value between 0 and 1.'
    )

    markup_cat_3 = models.FloatField(
        'Markup Segment 3',
        help_text='Percentage to be added over exchange rate for markup segment 3. Value between 0 and 1.'
    )

    markup_cat_4 = models.FloatField(
        'Markup Segment 4',
        help_text='Percentage to be added over exchange rate for markup segment 4. Value between 0 and 1.'
    )

    markup_cat_1_upper = models.IntegerField(
        'Upper bound of markup segment 1',
        help_text='Exclusive upper bound of markup segment 1 as value in USD.'
    )

    markup_cat_2_upper = models.IntegerField(
        'Upper bound of markup segment 2',
        help_text='Exclusive upper bound of markup segment 2 as value in USD.'
    )

    markup_cat_3_upper = models.IntegerField(
        'Upper bound of markup segment 3',
        help_text='Exclusive upper bound of markup segment 3 as value in USD.'
    )

    ghs_usd = models.FloatField(
        'GHS/USD Exchange Rate',
        help_text='Amount of GHS you get for 1 USD'
    )

    def __unicode__(self):
        return self.id

    @staticmethod
    def get_current_pricing():
        return Pricing.objects.get(end__isnull=True)

    @staticmethod
    def end_previous_pricing():
        try:
            previous_pricing = Pricing.objects.get(end__isnull=True)
            previous_pricing.end = timezone.now()
            previous_pricing.save()
        except ObjectDoesNotExist:
            pass

    def get_unit_price(self, amount_usd):
        if 1 <= amount_usd < self.markup_cat_1_upper:
            markup = self.markup_cat_1
        elif self.markup_cat_1_upper <= amount_usd < self.markup_cat_2_upper:
            markup = self.markup_cat_2
        elif self.markup_cat_2_upper <= amount_usd < self.markup_cat_3_upper:
            markup = self.markup_cat_3
        else:
            markup = self.markup_cat_4
        return math.floor(self.ghs_usd * (1 + markup) * 10) / 10


class Transaction(models.Model):

    class Meta:
        ordering = ['-initialized_at']

    # Constants
    INVALID = 'INVD'
    INIT = 'INIT'
    PAID = 'PAID'
    CANCELLED = 'CANC'
    DECLINED = 'DECL'
    PROCESSED = 'PROC'
    TRANSACTION_STATUS = (
        (INVALID, 'invalid'),
        (INIT, 'initialized'),
        (PAID, 'paid'),
        (CANCELLED, 'cancelled'),
        (DECLINED, 'declined'),
        (PROCESSED, 'processed'),
    )

    # Fields
    btc_wallet_address = models.CharField(
        'BTC Wallet Address',
        max_length=34,
        help_text='Wallet to send BTCs to. 27 - 34 alphanumeric characters'
    )
    notification_phone_number = models.CharField(
        'Notification Phone Number',
        max_length=15,
        help_text='Phone number for notification'
    )
    amount_ghs = models.FloatField(
        'GHS to Kitiwa',
        help_text='GHS to be paid to Kitiwa'
    )
    amount_usd = models.FloatField(
        'USD worth of BTC',
        help_text='USD worth of BTCs to be transferred to customer'
    )
    amount_btc = models.IntegerField(
        'Satoshi transferred',
        null=True,
        blank=True,
        help_text='BTCs transferred to the customer. amount_usd / exchange_rate in satoshi, rounded up.'
    )
    processed_exchange_rate = models.FloatField(
        'USD/BTC rate transfer rate',
        null=True,
        blank=True,
        help_text='Exchange rate used to convert usd to btc right before transferring (for time see field processed at)'
    )
    state = models.CharField(
        'State',
        max_length=4,
        choices=TRANSACTION_STATUS,
        default=INIT,
        help_text='State of the transaction'
    )
    initialized_at = models.DateTimeField(
        'Initialized at',
        auto_now_add=True,
        help_text='Time at which transaction was created by user'
    )
    paid_at = models.DateTimeField(
        'Paid at',
        null=True,
        blank=True,
        help_text='Time at which payment was confirmed with payment gateway'
    )
    processed_at = models.DateTimeField(
        'Processed at',
        null=True,
        blank=True,
        help_text='Time at which BTC were sent to customer'
    )
    cancelled_at = models.DateTimeField(
        'Cancelled at',
        null=True,
        blank=True,
        help_text='Time at which the customer cancelled the transaction'
    )
    declined_at = models.DateTimeField(
        'Declined at',
        null=True,
        blank=True,
        help_text='Time at which the transaction was declined by payment gateway'
    )
    penalty_in_usd = models.FloatField(
        'Penalty (USD)',
        blank=True,
        default=0.0,
        help_text='Penalty paid (in USD) due to delay in processing BTC transfer (processed at >>> paid at)'
    )
    pricing = models.ForeignKey(
        Pricing,
        related_name='transactions',
        help_text='Pricing information to enable amount_usd and amount_ghs relation (exchange rate and markup)'
    )

    reference_number = models.CharField(
        'Reference Number',
        max_length=6,
        help_text='6-digit reference number given to the customer to refer to transaction in case of problems'
    )

    transaction_uuid = models.CharField(
        "Transaction Identifier",
        max_length=36,
        blank=True,
        help_text='UUID version 4 to associate subsequent POST requests with a transaction.'
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

    # mpower specific fields
    smsgh_response_status = models.CharField(
        'Response code sent by SMSGH',
        max_length=5,
        blank=True,
        help_text='Code describing outcome of sending confirmation sms'
    )

    smsgh_message_id = models.CharField(
        'Message id sent by SMSGH',
        max_length=50,
        blank=True,
        help_text='Identifier referring to confirmation sms sent by SMSGH'
    )

    @staticmethod
    def calculate_ghs_price(amount_usd):
        unit_price = Pricing.get_current_pricing().get_unit_price(amount_usd)
        amount_ghs = math.floor(amount_usd * unit_price * 10) / 10
        return amount_ghs

    def generate_reference_number(self):
        self.reference_number = str(random.randint(10000, 999999))

    def save(self, *args, **kwargs):
        if is_valid_btc_address(self.btc_wallet_address):
            if not self.pk:
                self.pricing = Pricing.get_current_pricing()
                self.amount_ghs = Transaction.calculate_ghs_price(self.amount_usd)
                self.generate_reference_number()
            else:
                original = Transaction.objects.get(pk=self.pk)
                if original.pricing != self.pricing:
                    raise ValidationError('Pricing cannot be changed after initialization')
            super(Transaction, self).save(*args, **kwargs)
        else:
            raise ValidationError('Invalid BTC address')

    def update_btc(self, rate):
        self.amount_btc = int(math.ceil((self.amount_usd / rate) * ONE_SATOSHI))
        self.processed_exchange_rate = rate
        self.save()

    def update_after_opr_token_request(
            self, response_code, response_text,
            mpower_opr_token, mpower_invoice_token):

        self.mpower_response_code = response_code
        self.mpower_response_text = response_text

        if response_code == '00':
            self.mpower_opr_token = mpower_opr_token
            self.mpower_invoice_token = mpower_invoice_token
            self.transaction_uuid = uuid4()
        else:
            self.state = Transaction.INVALID
            self.declined_at = timezone.now()
        self.save()

    def update_after_opr_charge(self, response_code, response_text):

        self.mpower_response_code = response_code
        self.mpower_response_text = response_text

        if response_code == '00':
            self.state = Transaction.PAID
            self.paid_at = timezone.now()

        else:
            self.state = Transaction.DECLINED
            self.declined_at = timezone.now()

        self.save()

    def update_after_sms_notification(
            self, response_status, message_id):
        self.smsgh_response_status = response_status
        self.smsgh_message_id = message_id
        self.save()
