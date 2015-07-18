__author__ = 'parentj@eab.com (Jason Parent)'

# Third-party imports...
from rest_framework import serializers

# Local imports...
from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = (
            'id', 'first_name', 'last_name', 'address', 'email', 'num_attending', 'rsvp_date', 'waitlisted'
        )