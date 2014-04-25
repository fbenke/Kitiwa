from django.db import models


class Pricing(models.Model):

    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    markup = models.FloatField()
    ghs_usd = models.FloatField()

    def __unicode__(self):
        return '{pk} ({markup} %)'.format(pk=self.pk, markup=self.markup)

    @staticmethod
    def get_current_pricing():
        return Pricing.objects.get(end__isnull=True)


class Transaction(models.Model):

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
    # 27 - 34 alphanumeric characters
    btc_wallet_address = models.CharField(max_length=34,
                                          blank=True, default='')
    notification_phone_number = models.CharField(max_length=15)
    amount_ghs = models.FloatField()
    amount_usd = models.FloatField()
    state = models.CharField(max_length=4,
                             choices=TRANSACTION_STATUS, default=INIT)
    initialized_at = models.DateField(auto_now_add=True)
    paid_at = models.DateField(null=True, blank=True)
    processed_at = models.DateField(null=True, blank=True)
    cancelled_at = models.DateField(null=True, blank=True)
    declined_at = models.DateField(null=True, blank=True)
    penalty_in_usd = models.FloatField(blank=True, default=0.0)
    pricing = models.ForeignKey(Pricing, related_name='transactions')

    def save(self, *args, **kwargs):
        self.pricing = Pricing.get_current_pricing()
        super(Transaction, self).save(*args, **kwargs)
