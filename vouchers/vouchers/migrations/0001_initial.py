# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Voucher'
        db.create_table(u'vouchers_voucher', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('voucher_number1', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('voucher_number2', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('allocated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allocation_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'vouchers', ['Voucher'])

        # Adding model 'SurveyAllocation'
        db.create_table(u'vouchers_surveyallocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey_id', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('voucher', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='_surveyallocation', unique=True, null=True, to=orm['vouchers.Voucher'])),
        ))
        db.send_create_signal(u'vouchers', ['SurveyAllocation'])


    def backwards(self, orm):
        # Deleting model 'Voucher'
        db.delete_table(u'vouchers_voucher')

        # Deleting model 'SurveyAllocation'
        db.delete_table(u'vouchers_surveyallocation')


    models = {
        u'vouchers.surveyallocation': {
            'Meta': {'object_name': 'SurveyAllocation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'survey_id': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'voucher': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_surveyallocation'", 'unique': 'True', 'null': 'True', 'to': u"orm['vouchers.Voucher']"})
        },
        u'vouchers.voucher': {
            'Meta': {'object_name': 'Voucher'},
            'allocated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allocation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'voucher_number1': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'voucher_number2': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['vouchers']