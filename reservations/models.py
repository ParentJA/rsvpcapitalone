__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Standard library imports...
import json

# Third-party library imports...
from django_hstore import hstore

# Django imports...
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models


class Config(models.Model):
    data = hstore.DictionaryField(blank=True, null=True, schema=[{
        'name': 'MAX_NUM_RESERVATIONS',
        'class': 'IntegerField',
        'kwargs': {
            'default': 0
        }
    }, {
        'name': 'WAIT_LIST_MESSAGE',
        'class': 'TextField',
        'kwargs': {
            'blank': True
        }
    }, {
        'name': 'CONFIRMATION_MESSAGE',
        'class': 'TextField',
        'kwargs': {
            'blank': True
        }
    }])

    objects = hstore.HStoreManager()


class Reservation(models.Model):
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    email = models.EmailField(max_length=250, unique=True)
    num_attending = models.IntegerField(verbose_name='Number attending', max_length=1)
    rsvp_date = models.DateTimeField(verbose_name='RSVP date', auto_now=True)
    wait_listed = models.NullBooleanField(default=None)

    def save(self, *args, **kwargs):
        # Send email to admins: 'Update on reservations...'
        admins = [admin.email for admin in User.objects.filter(is_superuser=True)]

        body = '%s %s is confirmed for the event...' % (self.first_name, self.last_name)

        if self.wait_listed:
            body = '%s %s has been added to the wait list...' % (self.first_name, self.last_name,)

        send_mail(
            'Reservation',
            body,
            'rsvp@rsvpcapitalone.com',
            admins,
            fail_silently=True
        )

        super(Reservation, self).save(*args, **kwargs)

    def to_json(self):
        return json.dumps({
            'id': self.pk,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address': self.address,
            'email': self.email,
            'num_attending': self.num_attending,
            'wait_listed': self.wait_listed
        })

    def __unicode__(self):
        return 'Reservation for %s' % self.email