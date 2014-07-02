# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Reservation'
        db.create_table(u'reservations_reservation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=250)),
            ('num_attending', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('rsvp_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('waitlisted', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'reservations', ['Reservation'])


    def backwards(self, orm):
        # Deleting model 'Reservation'
        db.delete_table(u'reservations_reservation')


    models = {
        u'reservations.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '250'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'num_attending': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'rsvp_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'waitlisted': ('django.db.models.fields.BooleanField', [], {})
        }
    }

    complete_apps = ['reservations']