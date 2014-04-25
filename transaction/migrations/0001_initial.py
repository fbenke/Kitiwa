# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Pricing'
        db.create_table(u'transaction_pricing', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('markup', self.gf('django.db.models.fields.FloatField')()),
            ('ghs_usd', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'transaction', ['Pricing'])

        # Adding model 'Transaction'
        db.create_table(u'transaction_transaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=30, blank=True)),
            ('btc_wallet_address', self.gf('django.db.models.fields.CharField')(max_length=34, blank=True)),
            ('notification_phone_number', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('amount_ghs', self.gf('django.db.models.fields.FloatField')()),
            ('amount_usd', self.gf('django.db.models.fields.FloatField')()),
            ('state', self.gf('django.db.models.fields.CharField')(default='INIT', max_length=4)),
            ('initialized_at', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('paid_at', self.gf('django.db.models.fields.DateField')(null=True)),
            ('processed_at', self.gf('django.db.models.fields.DateField')(null=True)),
            ('cancelled_at', self.gf('django.db.models.fields.DateField')(null=True)),
            ('declined_at', self.gf('django.db.models.fields.DateField')(null=True)),
            ('penalty_in_usd', self.gf('django.db.models.fields.FloatField')(default=0.0, blank=True)),
            ('pricing', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transactions', to=orm['transaction.Pricing'])),
        ))
        db.send_create_signal(u'transaction', ['Transaction'])


    def backwards(self, orm):
        # Deleting model 'Pricing'
        db.delete_table(u'transaction_pricing')

        # Deleting model 'Transaction'
        db.delete_table(u'transaction_transaction')


    models = {
        u'transaction.pricing': {
            'Meta': {'object_name': 'Pricing'},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'ghs_usd': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.FloatField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'transaction.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'amount_ghs': ('django.db.models.fields.FloatField', [], {}),
            'amount_usd': ('django.db.models.fields.FloatField', [], {}),
            'btc_wallet_address': ('django.db.models.fields.CharField', [], {'max_length': '34', 'blank': 'True'}),
            'cancelled_at': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'declined_at': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '30', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initialized_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'notification_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'paid_at': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'penalty_in_usd': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['transaction.Pricing']"}),
            'processed_at': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'INIT'", 'max_length': '4'})
        }
    }

    complete_apps = ['transaction']