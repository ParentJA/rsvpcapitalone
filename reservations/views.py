from django.core.mail import send_mail
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

import json

from reservations.models import Reservation

from rsvpcapitalone.settings import MAX_NUM_RESERVATIONS


@ensure_csrf_cookie
def home(request):
    return render(request, 'home.html')


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
                email = email.lower()

                selected_reservation = Reservation.objects.get(id=reservation_id, email=email)
                selected_reservation.waitlisted = True
                selected_reservation.save()

                # Send email: 'You have been added to the waitlist...'
                send_mail(
                    'Reservation',
                    'Thanks for your response to the Celebrity Chef Event.\n\n'
                    'Unfortunately we have reached capacity for this event, but if requested, '
                    'you have been added to the waitlist.\n\n'
                    'We will contact you if space opens.\n\n'
                    'Thank you again.\n\n'
                    'Capital One Bank',
                    'rsvp@rsvpcapitalone.com',
                    [email],
                    fail_silently=True
                )

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
                'Your reservation for the Celebrity Chef Event is confirmed!\n\n'
                'We look forward to seeing you at the branch at 7pm. 750 Columbus Avenue\n\n'
                'New York, NY 10025\n\n'
                'Thank you,\n\n'
                'Capital One Bank',
                'rsvp@rsvpcapitalone.com',
                [email],
                fail_silently=True
            )

            return HttpResponse(selected_reservation.to_json())

    return HttpResponseNotAllowed(['GET', 'POST'])