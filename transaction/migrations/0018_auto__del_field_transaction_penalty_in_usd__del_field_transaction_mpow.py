# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Transaction.penalty_in_usd'
        db.delete_column(u'transaction_transaction', 'penalty_in_usd')

        # Deleting field 'Transaction.mpower_response_text'
        db.delete_column(u'transaction_transaction', 'mpower_response_text')

        # Deleting field 'Transaction.mpower_invoice_token'
        db.delete_column(u'transaction_transaction', 'mpower_invoice_token')

        # Deleting field 'Transaction.mpower_confirm_token'
        db.delete_column(u'transaction_transaction', 'mpower_confirm_token')

        # Deleting field 'Transaction.mpower_opr_token'
        db.delete_column(u'transaction_transaction', 'mpower_opr_token')

        # Deleting field 'Transaction.mpower_response_code'
        db.delete_column(u'transaction_transaction', 'mpower_response_code')

        # Adding field 'Transaction.amount_ngn'
        db.add_column(u'transaction_transaction', 'amount_ngn',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Transaction.payment_type'
        db.add_column(u'transaction_transaction', 'payment_type',
                      self.gf('django.db.models.fields.CharField')(default=0, max_length=4),
                      keep_default=False)


        # Changing field 'Transaction.reference_number'
        db.alter_column(u'transaction_transaction', 'reference_number', self.gf('django.db.models.fields.CharField')(max_length=10))

        # Changing field 'Transaction.amount_ghs'
        db.alter_column(u'transaction_transaction', 'amount_ghs', self.gf('django.db.models.fields.FloatField')(null=True))
        # Adding field 'Pricing.ngn_usd'
        db.add_column(u'transaction_pricing', 'ngn_usd',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Transaction.penalty_in_usd'
        db.add_column(u'transaction_transaction', 'penalty_in_usd',
                      self.gf('django.db.models.fields.FloatField')(default=0.0, blank=True),
                      keep_default=False)

        # Adding field 'Transaction.mpower_response_text'
        db.add_column(u'transaction_transaction', 'mpower_response_text',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Transaction.mpower_invoice_token'
        db.add_column(u'transaction_transaction', 'mpower_invoice_token',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True),
                      keep_default=False)

        # Adding field 'Transaction.mpower_confirm_token'
        db.add_column(u'transaction_transaction', 'mpower_confirm_token',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'Transaction.mpower_opr_token'
        db.add_column(u'transaction_transaction', 'mpower_opr_token',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True),
                      keep_default=False)

        # Adding field 'Transaction.mpower_response_code'
        db.add_column(u'transaction_transaction', 'mpower_response_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Deleting field 'Transaction.amount_ngn'
        db.delete_column(u'transaction_transaction', 'amount_ngn')

        # Deleting field 'Transaction.payment_type'
        db.delete_column(u'transaction_transaction', 'payment_type')


        # Changing field 'Transaction.reference_number'
        db.alter_column(u'transaction_transaction', 'reference_number', self.gf('django.db.models.fields.CharField')(max_length=6))

        # Changing field 'Transaction.amount_ghs'
        db.alter_column(u'transaction_transaction', 'amount_ghs', self.gf('django.db.models.fields.FloatField')(default=0))
        # Deleting field 'Pricing.ngn_usd'
        db.delete_column(u'transaction_pricing', 'ngn_usd')


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