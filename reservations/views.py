from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden

import json

from reservations.models import Reservation

from rsvpcapitalone.settings import MAX_NUM_RESERVATIONS


def api_reservations(request, reservation_id=None):
    if request.method == 'GET':
        if request.user.is_superuser():
            # Get a single reservation by ID...
            if reservation_id:
                pass

            # Get all reservations...
            else:
                pass

        else:
            return HttpResponseForbidden('You must have superuser privileges to access this information.')

    elif request.method == 'POST':
        data = request.POST

        if len(data) == 0:
            try:
                data = json.dumps(request.body)
            except ValueError:
                return HttpResponseBadRequest('You must call the API with properly formatted parameters.')

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        address = data.get('address')
        email = data.get('email')
        num_attending = int(data.get('num_attending'))

        if not all(first_name, last_name, address, email, num_attending):
            return HttpResponseBadRequest(
                'You must provide all of the required parameters: first_name, last_name, address, \
                email, num_attending.'
            )

        # Updating specific reservation with waitlist choice...
        if reservation_id:
            pass

        # Add a new reservation...
        else:
            current_reservations = Reservation.objects.all()
            num_reservations = len(current_reservations)
            existing_reservation = current_reservations.filter(email=email)

            # Only create a new reservation if one does already exist...
            if not existing_reservation.exists():
                num_reservations += 1
                existing_reservation = Reservation.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    email=email,
                    num_attending=min(2, max(1, num_attending))
                )

            # Make sure the maximum number of reservations has not been exceeded...
            if num_reservations > MAX_NUM_RESERVATIONS:
                existing_reservation.waitlisted = False
                existing_reservation.save()

            return HttpResponse(existing_reservation.to_json())

    return HttpResponse()