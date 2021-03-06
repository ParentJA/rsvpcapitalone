__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Standard-library imports...
import json

# Third-party library imports...
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# Django imports...
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.utils.decorators import method_decorator

# Local imports...
from .forms import ReservationForm
from .models import Reservation
from .serializers import ReservationSerializer
from .utils import get_param

user_is_superuser = user_passes_test(lambda u: u.is_superuser, login_url='/admin/')

MAX_NUM_RESERVATIONS = get_param('MAX_NUM_RESERVATIONS', 66)
WAIT_LIST_MESSAGE = get_param('WAIT_LIST_MESSAGE', '[WAIT_LIST_MESSAGE]')
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
            reservation_form = ReservationForm(request.data)

            if reservation_form.is_valid():
                reservation = reservation_form.save()
                num_reservations += reservation.num_attending

            else:
                return Response(data=json.dumps(reservation_form.errors), status_code=400)

        # Make sure the maximum number of reservations has not been exceeded...
        if num_reservations > int(MAX_NUM_RESERVATIONS):
            reservation.wait_listed = False
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
        reservation.wait_listed = True
        reservation.save()

        # Send email: 'You have been added to the wait list...'
        send_mail(
            'Reservation',
            message=WAIT_LIST_MESSAGE,
            from_email='rsvp@rsvpcapitalone.com',
            recipient_list=[reservation.email],
            fail_silently=True
        )

        return Response(data=ReservationSerializer(reservation).data)