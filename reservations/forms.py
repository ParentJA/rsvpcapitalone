__author__ = 'parentj@eab.com (Jason Parent)'

# Django imports...
from django import forms

# Local imports...
from .models import Reservation


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('first_name', 'last_name', 'address', 'email', 'num_attending')