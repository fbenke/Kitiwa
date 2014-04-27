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

    def end_previous_pricing(self):
        try:
            previous_pricing = Pricing.objects.get(end__isnull=True)
            previous_pricing.end = datetime.now()
            previous_pricing.save()
        except ObjectDoesNotExist:
            pass


class Transaction(models.Model):

    class Meta:
        ordering = ['id']

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

    email = models.EmailField(max_length=30, blank=True, default='')
    btc_wallet_address = models.CharField(max_length=34,
                                          blank=True, default='')
    notification_phone_number = models.CharField(max_length=15)
    amount_ghs = models.FloatField()
    amount_usd = models.FloatField()
    state = models.CharField(max_length=4,
                             choices=TRANSACTION_STATUS, default=INIT)
    initialized_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    penalty_in_usd = models.FloatField(blank=True, default=0.0)
    pricing = models.ForeignKey(Pricing, related_name='transactions')

    # mpower specific fields
    mpower_token = models.CharField(max_length=30, blank=True, default='')

    def save(self, *args, **kwargs):
        self.pricing = Pricing.get_current_pricing()
        super(Transaction, self).save(*args, **kwargs)
