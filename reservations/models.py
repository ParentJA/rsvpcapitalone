from django.db import models

import json


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