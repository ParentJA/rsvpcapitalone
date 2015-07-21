# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Reservation.waitlisted'
        db.delete_column(u'reservations_reservation', 'waitlisted')

        # Adding field 'Reservation.wait_listed'
        db.add_column(u'reservations_reservation', 'wait_listed',
                      self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Reservation.waitlisted'
        db.add_column(u'reservations_reservation', 'waitlisted',
                      self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Reservation.wait_listed'
        db.delete_column(u'reservations_reservation', 'wait_listed')


    models = {
        u'reservations.config': {
            'Meta': {'object_name': 'Config'},
            'data': (u'django_hstore.fields.DictionaryField', [], {u'default': None, 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'reservations.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '250'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'num_attending': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'rsvp_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'wait_listed': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['reservations']