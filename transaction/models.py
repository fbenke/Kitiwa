from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


class Pricing(models.Model):

    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(blank=True, null=True)
    markup = models.FloatField()
    ghs_usd = models.FloatField()

    def __unicode__(self):
        return '{markup} %'.format(markup=self.markup)

    @staticmethod
    def get_current_pricing():
        return Pricing.objects.get(end__isnull=True)

    @staticmethod
    def end_previous_pricing():
        try:
            previous_pricing = Pricing.objects.get(end__isnull=True)
            previous_pricing.end = datetime.now()
            previous_pricing.save()
        except ObjectDoesNotExist:
            pass


class Transaction(models.Model):

    class Meta:
        ordering = ['id']

    # Constants
    INIT = 'INIT'
    PAID = 'PAID'
    CANCELLED = 'CANC'
    DECLINED = 'DECL'
    PROCESSED = 'PROC'
    TRANSACTION_STATUS = (
        (INIT, 'initialized'),
        (PAID, 'paid'),
        (CANCELLED, 'cancelled'),
        (DECLINED, 'declined'),
        (PROCESSED, 'processed'),
    )

    # Fields
    email = models.EmailField(
        'Email',
        max_length=30,
        blank=True,
        default='',
        help_text='Email to send BTCs to'
    )
    btc_wallet_address = models.CharField(
        'BTC Wallet Address',
        max_length=34,
        blank=True,
        default='',
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

    # mpower specific fields
    mpower_token = models.CharField(
        'MPower Token',
        max_length=30,
        blank=True,
        default=''
    )

    def save(self, *args, **kwargs):
        self.pricing = Pricing.get_current_pricing()
        usd_in_ghs = self.amount_usd * self.pricing.ghs_usd
        self.amount_ghs = usd_in_ghs * (1 + self.pricing.markup)
        super(Transaction, self).save(*args, **kwargs)
