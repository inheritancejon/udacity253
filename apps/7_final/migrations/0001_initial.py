# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WikiPage'
        db.create_table('7_final_wikipage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page_url', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('7_final', ['WikiPage'])

        # Adding model 'WikiPageHistory'
        db.create_table('7_final_wikipagehistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['7_final.WikiPage'])),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('7_final', ['WikiPageHistory'])


    def backwards(self, orm):
        # Deleting model 'WikiPage'
        db.delete_table('7_final_wikipage')

        # Deleting model 'WikiPageHistory'
        db.delete_table('7_final_wikipagehistory')


    models = {
        '7_final.wikipage': {
            'Meta': {'object_name': 'WikiPage'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page_url': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        '7_final.wikipagehistory': {
            'Meta': {'object_name': 'WikiPageHistory'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['7_final.WikiPage']"}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['7_final']