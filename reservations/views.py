from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404

import json

from reservations.models import Reservation

from rsvpcapitalone.settings import MAX_NUM_RESERVATIONS


def api_reservations(request, reservation_id=None):
    if request.method == 'GET':
        if request.user.is_superuser:
            # Get a single reservation by ID...
            if reservation_id:
                selected_reservation = get_object_or_404(Reservation, pk=reservation_id)

                return HttpResponse(selected_reservation.to_json())

            # Get all reservations...
            else:
                return HttpResponse(
                    json.dumps([reservation.to_json() for reservation in Reservation.objects.all()])
                )

        else:
            return HttpResponseForbidden('You must have superuser privileges to access this information.')

    elif request.method == 'POST':
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
                selected_reservation = Reservation.objects.get(id=reservation_id, email=email)
                selected_reservation.waitlist = True
                selected_reservation.save()

                return HttpResponse()

            except Reservation.DoesNotExist:
                return HttpResponseNotFound('A reservation with the given ID and email was not found.')

        # Add a new reservation...
        else:
            if not all([first_name, last_name, address, email, num_attending]):
                return HttpResponseBadRequest(
                    'You must provide all of the required parameters: first_name, last_name, address, \
                    email, num_attending.'
                )

            current_reservations = Reservation.objects.all()
            num_reservations = len(current_reservations)
            existing_reservation = current_reservations.filter(email=email.lower())
            selected_reservation = None

            # Only create a new reservation if one does not already exist...
            if existing_reservation.exists():
                selected_reservation = existing_reservation[0]
            else:
                num_reservations += 1
                selected_reservation = Reservation.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    email=email.lower(),
                    num_attending=min(2, max(1, int(num_attending)))
                )

            # Make sure the maximum number of reservations has not been exceeded...
            if num_reservations > MAX_NUM_RESERVATIONS:
                selected_reservation.waitlisted = False
                selected_reservation.save()

            return HttpResponse(selected_reservation.to_json())

    return HttpResponseNotAllowed(['GET', 'POST'])