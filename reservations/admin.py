from django.contrib import admin

from reservations.models import Reservation


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('rsvp_date', 'first_name', 'last_name', 'address', 'email', 'num_attending', 'waitlisted',)


admin.site.register(Reservation, ReservationAdmin)