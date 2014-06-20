# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Pricing.markup'
        db.delete_column(u'transaction_pricing', 'markup')


    def backwards(self, orm):
        # Adding field 'Pricing.markup'
        db.add_column(u'transaction_pricing', 'markup',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)


    models = {
        u'transaction.pricing': {
            'Meta': {'object_name': 'Pricing'},
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ghs_usd': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup_cat_1': ('django.db.models.fields.FloatField', [], {}),
            'markup_cat_2': ('django.db.models.fields.FloatField', [], {}),
            'markup_cat_3': ('django.db.models.fields.FloatField', [], {}),
            'markup_cat_4': ('django.db.models.fields.FloatField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'transaction.transaction': {
            'Meta': {'ordering': "['-initialized_at']", 'object_name': 'Transaction'},
            'amount_btc': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amount_ghs': ('django.db.models.fields.FloatField', [], {}),
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
            'penalty_in_usd': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['transaction.Pricing']"}),
            'processed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'processed_exchange_rate': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'reference_number': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'smsgh_message_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'smsgh_response_status': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'INIT'", 'max_length': '4'}),
            'transaction_uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        }
    }

    complete_apps = ['transaction']