# -*- coding: utf-8 -*-
from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        "Manually written forwards method."
        for transaction in orm.Transaction.objects.all():
            payment = orm['payment.MPowerPayment'].objects.create(
                mpower_opr_token=transaction.mpower_opr_token,
                mpower_confirm_token=transaction.mpower_confirm_token,
                mpower_invoice_token=transaction.mpower_invoice_token,
                mpower_response_code=transaction.mpower_response_code,
                mpower_response_text=transaction.mpower_response_text,
                transaction=transaction
            )
            payment.save()

    def backwards(self, orm):
        "Manually written forwards method."
        for payment in orm['payment.MPowerPayment'].objects.all():
            transaction = orm.Transaction.objects.get(id=payment.transaction.id)
            transaction.mpower_opr_token = payment.mpower_opr_token
            transaction.mpower_confirm_token = payment.mpower_confirm_token
            transaction.mpower_invoice_token = payment.mpower_invoice_token
            transaction.mpower_response_code = payment.mpower_response_code
            transaction.mpower_response_text = payment.mpower_response_text
            transaction.save()

    models = {
        u'payment.mpowerpayment': {
            'Meta': {'object_name': 'MPowerPayment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mpower_confirm_token': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'mpower_invoice_token': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mpower_opr_token': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mpower_response_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'mpower_response_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mpower_payments'", 'to': u"orm['transaction.Transaction']"})
        },
        u'transaction.pricing': {
            'Meta': {'object_name': 'Pricing'},
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ghs_usd': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup_cat_1': ('django.db.models.fields.FloatField', [], {}),
            'markup_cat_1_upper': ('django.db.models.fields.IntegerField', [], {}),
            'markup_cat_2': ('django.db.models.fields.FloatField', [], {}),
            'markup_cat_2_upper': ('django.db.models.fields.IntegerField', [], {}),
            'markup_cat_3': ('django.db.models.fields.FloatField', [], {}),
            'markup_cat_3_upper': ('django.db.models.fields.IntegerField', [], {}),
            'markup_cat_4': ('django.db.models.fields.FloatField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'transaction.transaction': {
            'Meta': {'ordering': "['-initialized_at']", 'object_name': 'Transaction'},
            'amount_btc': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amount_ghs': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'amount_ngn': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'amount_usd': ('django.db.models.fields.FloatField', [], {}),
            'btc_wallet_address': ('django.db.models.fields.CharField', [], {'max_length': '34'}),
            'cancelled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'declined_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initialized_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'mpower_confirm_token': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'mpower_invoice_token': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mpower_opr_token': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mpower_response_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'mpower_response_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'notification_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'paid_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'payment_type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['transaction.Pricing']"}),
            'processed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'processed_exchange_rate': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'reference_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'smsgh_message_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'smsgh_response_status': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'INIT'", 'max_length': '4'}),
            'transaction_uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        }
    }

    complete_apps = ['payment', 'transaction']
    symmetrical = True
