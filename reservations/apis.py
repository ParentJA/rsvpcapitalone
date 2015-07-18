__author__ = 'parentj@eab.com (Jason Parent)'

# Standard library imports...
import json

# Third-party library imports...
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

    @method_decorator(user_is_superuser)
    def retrieve(self, request, pk=None):
        return super(ReservationViewSet, self).retrieve(request, pk)


def api_reservations(request, reservation_id=None):
    data = request.POST

    if len(data) == 0:
        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest('You must call the API with properly formatted parameters.')

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    address = data.get('address')
    email = data.get('email')
    num_attending = data.get('num_attending')

    # Updating specific reservation with waitlist choice...
    if reservation_id:
        if not email:
            return HttpResponseBadRequest('You must provide the email associated with the reservation ID.')

        try:
            email = email.lower()

            selected_reservation = Reservation.objects.get(id=reservation_id, email=email)
            selected_reservation.waitlisted = True
            selected_reservation.save()

            # Send email: 'You have been added to the waitlist...'
            send_mail(
                'Reservation',
                message=WAITLIST_MESSAGE,
                from_email='rsvp@rsvpcapitalone.com',
                recipient_list=[email],
                fail_silently=True
            )

            return HttpResponse()

        except Reservation.DoesNotExist:
            return HttpResponseNotFound('A reservation with the given ID and email was not found.')

    # Add a new reservation...
    else:
        if not all([first_name, last_name, address, email, num_attending]):
            return HttpResponseBadRequest(''.join([
                'You must provide all of the required parameters: first_name, last_name, address,',
                'email, num_attending.'
            ]))

        email = email.lower()

        current_reservations = Reservation.objects.all()
        num_reservations = sum([reservation.num_attending for reservation in current_reservations])
        existing_reservation = current_reservations.filter(email=email)
        selected_reservation = None

        # Only create a new reservation if one does not already exist...
        if existing_reservation.exists():
            selected_reservation = existing_reservation[0]
        else:
            try:
                num_attending = int(num_attending)
                num_attending = max(1, num_attending)
                num_attending = min(2, num_attending)
            except ValueError:
                num_attending = 1

            selected_reservation = Reservation.objects.create(
                first_name=first_name,
                last_name=last_name,
                address=address,
                email=email,
                num_attending=num_attending
            )

            num_reservations += selected_reservation.num_attending

        # Make sure the maximum number of reservations has not been exceeded...
        if num_reservations > MAX_NUM_RESERVATIONS:
            selected_reservation.waitlisted = False
            selected_reservation.save()

        # Send email: 'You are confirmed for the event...'
        send_mail(
            'Reservation',
            message=CONFIRMATION_MESSAGE,
            from_email='rsvp@rsvpcapitalone.com',
            recipient_list=[email],
            fail_silently=True
        )

        return HttpResponse(selected_reservation.to_json())