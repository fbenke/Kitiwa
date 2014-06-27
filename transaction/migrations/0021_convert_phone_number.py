# -*- coding: utf-8 -*-
from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        for transaction in orm.Transaction.objects.all():
            if transaction.notification_phone_number[0] == '0' and transaction.payment_type == '0':
                transaction.notification_phone_number =\
                    '+233{}'.format(transaction.notification_phone_number[1::])
                transaction.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        pass

    models = {
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
            'ngn_usd': ('django.db.models.fields.FloatField', [], {}),
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

    complete_apps = ['transaction']
    symmetrical = True
