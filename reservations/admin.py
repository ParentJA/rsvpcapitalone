__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Django imports...
from django.contrib import admin

# Local imports...
from reservations.models import Config, Reservation


class ConfigAdmin(admin.ModelAdmin):
    pass

admin.site.register(Config, ConfigAdmin)


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('rsvp_date', 'first_name', 'last_name', 'address', 'email', 'num_attending', 'wait_listed',)

admin.site.register(Reservation, ReservationAdmin)