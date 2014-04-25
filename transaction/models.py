from django.db import models


class Pricing(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    markup = models.FloatField()
    ghs_usd = models.FloatField()


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

    email = models.EmailField(max_length=30, blank=True)
    # 27 - 34 alphanumeric characters
    btc_wallet_address = models.CharField(max_length=34, blank=True)
    notification_phone_number = models.CharField(max_length=15)
    amount_ghs = models.FloatField()
    amount_usd = models.FloatField()
    state = models.CharField(max_length=4,
                             choices=TRANSACTION_STATUS, default=INIT)
    initialized_at = models.DateField(auto_now_add=True)
    paid_at = models.DateField(null=True)
    processed_at = models.DateField(null=True)
    cancelled_at = models.DateField(null=True)
    declined_at = models.DateField(null=True)
    penalty_in_usd = models.FloatField(default=0.0, blank=True)
    pricing = models.ForeignKey(Pricing, related_name='transactions',
                                null=True)
