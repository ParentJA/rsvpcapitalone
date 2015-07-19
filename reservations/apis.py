__author__ = 'parentj@eab.com (Jason Parent)'

# Standard library imports...
import json

# Third-party library imports...
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# Django imports...
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
)
from django.utils.decorators import method_decorator

# Local imports...
from .models import Reservation
from .serializers import ReservationSerializer
from .utils import get_param

user_is_superuser = user_passes_test(lambda u: u.is_superuser, login_url='/admin/')

MAX_NUM_RESERVATIONS = int(get_param('MAX_NUM_RESERVATIONS', 66))
WAITLIST_MESSAGE = get_param('WAITLIST_MESSAGE', '[WAITLIST_MESSAGE]')
CONFIRMATION_MESSAGE = get_param('CONFIRMATION_MESSAGE', '[CONFIRMATION_MESSAGE]')


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    @method_decorator(user_is_superuser)
    def list(self, request):
        return super(ReservationViewSet, self).list(request)

    def create(self, request):
        current_reservations = self.get_queryset()
        num_reservations = sum([reservation.num_attending for reservation in current_reservations])
        reservations_matching_email = current_reservations.filter(email=request.data.get('email'))

        if reservations_matching_email.exists():
            reservation = reservations_matching_email.first()

        else:
            try:
                num_attending = int(request.data.get('num_attending', 1))
                num_attending = max(1, num_attending)
                num_attending = min(2, num_attending)
            except ValueError:
                num_attending = 1

            reservation = Reservation(**request.data)
            reservation.num_attending = num_attending
            reservation.save()

            num_reservations += reservation.num_attending

        # Make sure the maximum number of reservations has not been exceeded...
        if num_reservations > MAX_NUM_RESERVATIONS:
            reservation.waitlisted = False
            reservation.save()

        # Send email: 'You are confirmed for the event...'
        send_mail(
            'Reservation',
            message=CONFIRMATION_MESSAGE,
            from_email='rsvp@rsvpcapitalone.com',
            recipient_list=[request.data.get('email')],
            fail_silently=True
        )

        return Response(data=ReservationSerializer(reservation).data)


    @method_decorator(user_is_superuser)
    def retrieve(self, request, pk=None):
        return super(ReservationViewSet, self).retrieve(request, pk)

    def update(self, request, pk=None):
        reservation = get_object_or_404(Reservation, pk=pk)
        reservation.waitlisted = True
        reservation.save()

        # Send email: 'You have been added to the waitlist...'
        send_mail(
            'Reservation',
            message=WAITLIST_MESSAGE,
            from_email='rsvp@rsvpcapitalone.com',
            recipient_list=[reservation.email],
            fail_silently=True
        )

        return Response(data=ReservationSerializer(reservation).data)