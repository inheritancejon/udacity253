# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'WikiPageHistory.date_created'
        db.add_column('7_final_wikipagehistory', 'date_created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 6, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'WikiPageHistory.date_created'
        db.delete_column('7_final_wikipagehistory', 'date_created')


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