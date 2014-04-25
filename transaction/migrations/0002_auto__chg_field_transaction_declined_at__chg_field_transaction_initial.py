# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Transaction.declined_at'
        db.alter_column(u'transaction_transaction', 'declined_at', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Transaction.initialized_at'
        db.alter_column(u'transaction_transaction', 'initialized_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'Transaction.cancelled_at'
        db.alter_column(u'transaction_transaction', 'cancelled_at', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Transaction.processed_at'
        db.alter_column(u'transaction_transaction', 'processed_at', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Transaction.paid_at'
        db.alter_column(u'transaction_transaction', 'paid_at', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):

        # Changing field 'Transaction.declined_at'
        db.alter_column(u'transaction_transaction', 'declined_at', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Transaction.initialized_at'
        db.alter_column(u'transaction_transaction', 'initialized_at', self.gf('django.db.models.fields.DateField')(auto_now_add=True))

        # Changing field 'Transaction.cancelled_at'
        db.alter_column(u'transaction_transaction', 'cancelled_at', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Transaction.processed_at'
        db.alter_column(u'transaction_transaction', 'processed_at', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Transaction.paid_at'
        db.alter_column(u'transaction_transaction', 'paid_at', self.gf('django.db.models.fields.DateField')(null=True))

    models = {
        u'transaction.pricing': {
            'Meta': {'object_name': 'Pricing'},
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ghs_usd': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.FloatField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'transaction.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'amount_ghs': ('django.db.models.fields.FloatField', [], {}),
            'amount_usd': ('django.db.models.fields.FloatField', [], {}),
            'btc_wallet_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '34', 'blank': 'True'}),
            'cancelled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'declined_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initialized_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'notification_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'paid_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'penalty_in_usd': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['transaction.Pricing']"}),
            'processed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'INIT'", 'max_length': '4'})
        }
    }

    complete_apps = ['transaction']