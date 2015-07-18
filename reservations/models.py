__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Standard library imports...
import json

# Django imports...
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models

DEBUG = getattr(settings, 'DEBUG', False)


class Reservation(models.Model):
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    email = models.EmailField(max_length=250, unique=True)
    num_attending = models.IntegerField(verbose_name='Number attending', max_length=1)
    rsvp_date = models.DateTimeField(verbose_name='RSVP date', auto_now=True)
    waitlisted = models.NullBooleanField(default=None)

    def save(self, *args, **kwargs):
        # Send email to admins: 'Update on reservations...'
        admins = [admin.email for admin in User.objects.filter(is_superuser=True)]

        body = '%s %s is confirmed for the event...' % (self.first_name, self.last_name)

        if self.waitlisted:
            body = '%s %s has been added to the waitlist...' % (self.first_name, self.last_name,)

        if not DEBUG:
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
            'waitlisted': self.waitlisted
        })

    def __unicode__(self):
        return 'Reservation for %s' % self.email