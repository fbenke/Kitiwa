from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone

from kitiwa.settings import ONE_SATOSHI
from kitiwa.utils import log_error

from transaction.utils import is_valid_btc_address

from uuid import uuid4
import math
import random
# TODO: move constants to settings file?


class Pricing(models.Model):

    GHS = '0'
    NGN = '1'
    EXCHANGE_RATES = (GHS, NGN, )

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

    ngn_usd = models.FloatField(
        'NGN/USD Exchange Rate',
        help_text='Amount of NGN you get for 1 USD'
    )

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
            log_error('ERROR - Failed to end previous pricing.')

    def _get_exchange_rate(self, currency):
        if currency == Pricing.GHS:
            return self.ghs_usd
        elif currency == Pricing.NGN:
            return self.ngn_usd
        else:
            return None

    def get_unit_price(self, amount_usd, currency):
        if currency not in Pricing.EXCHANGE_RATES:
            return None
        exchange_rate = self._get_exchange_rate(currency)

        if 1 <= amount_usd < self.markup_cat_1_upper:
            markup = self.markup_cat_1
        elif self.markup_cat_1_upper <= amount_usd < self.markup_cat_2_upper:
            markup = self.markup_cat_2
        elif self.markup_cat_2_upper <= amount_usd < self.markup_cat_3_upper:
            markup = self.markup_cat_3
        else:
            markup = self.markup_cat_4

        return math.floor(exchange_rate * (1 + markup) * 10) / 10

    def __unicode__(self):
        return '{}'.format(self.id)


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

    MPOWER = '0'
    PAGA = '1'

    PAYMENT_PROVIDER = (MPOWER, PAGA, )

    PAYMENT_TYPE = (
        (MPOWER, 'mpower'),
        (PAGA, 'paga'),
    )

    CURRENCY = {
        MPOWER: Pricing.GHS,
        PAGA: Pricing.NGN
    }

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
        null=True,
        help_text='GHS to be paid to Kitiwa'
    )
    amount_ngn = models.FloatField(
        'NGN to Kitiwa',
        null=True,
        help_text='NGN to be paid to Kitiwa'
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
    reference_number = models.CharField(
        'Reference Number',
        max_length=10,
        help_text='6-digit reference number given to the customer to refer to transaction in case of problems'
    )
    transaction_uuid = models.CharField(
        "Transaction Identifier",
        max_length=36,
        blank=True,
        help_text='UUID version 4 to associate payment with a transaction.'
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
    payment_type = models.CharField(
        'Payment Type',
        max_length=4,
        choices=PAYMENT_TYPE,
        help_text='Payment Method used for the transaction'
    )
    pricing = models.ForeignKey(
        Pricing,
        related_name='transactions',
        help_text='Pricing information to enable amount_usd, amount_ghs, amount_ngn relation (exchange rates and markup)'
    )
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

    def __unicode__(self):
        return '{}'.format(self.id)

    def _set_local_price(self):
        if self.payment_type not in Transaction.PAYMENT_PROVIDER:
            return
        local_price = Transaction.calculate_local_price(self.amount_usd, self.payment_type)
        if self.payment_type == Transaction.MPOWER:
            self.amount_ghs = local_price
        elif self.payment_type == Transaction.PAGA:
            self.ngn_usd = local_price

    def _generate_reference_number(self):
        self.reference_number = str(random.randint(10000, 999999))

    @staticmethod
    def calculate_local_price(amount_usd, payment_type):
        currency = Transaction.CURRENCY[payment_type]
        unit_price = Pricing.get_current_pricing().get_unit_price(amount_usd, currency)
        return math.floor(amount_usd * unit_price * 10) / 10

    def save(self, *args, **kwargs):
        if is_valid_btc_address(self.btc_wallet_address):
            if not self.pk:
                self.pricing = Pricing.get_current_pricing()
                self._set_local_price()
                self._generate_reference_number()
                self.transaction_uuid = uuid4()
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

    def update_after_sms_notification(
            self, response_status, message_id):
        self.smsgh_response_status = response_status
        self.smsgh_message_id = message_id
        self.save()
