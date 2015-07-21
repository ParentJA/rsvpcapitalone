__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Standard library imports...
import json

# Third-party imports...
from mock import patch
from rest_framework.test import APIClient

# Django imports...
from django.contrib.auth import get_user_model
from django.test import TestCase

# Local imports...
from ..apis import CONFIRMATION_MESSAGE, WAIT_LIST_MESSAGE
from ..models import Reservation
from ..serializers import ReservationSerializer

User = get_user_model()


class ReservationsViewTest(TestCase):
    fixtures = ['reservations']

    def setUp(self):
        self.client = APIClient()

        # Create a superuser...
        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='password',
            email='superuser@example.com'
        )

        # Get the reservation installed by the fixture...
        self.reservation = Reservation.objects.first()

    def test_user_cannot_retrieve_reservations(self):
        response = self.client.get('/api/v1/reservations/')

        self.assertRedirects(response, '/admin/?next=/api/v1/reservations/')

    def test_user_cannot_list_reservations(self):
        response = self.client.get('/api/v1/reservations/%d/' % (self.reservation.id,))

        self.assertRedirects(response, '/admin/?next=/api/v1/reservations/%d/' % (self.reservation.id,))

    def test_superuser_can_retrieve_existing_reservation(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.get('/api/v1/reservations/%d/' % (self.reservation.id,))

        self.assertJSONEqual(response.content, ReservationSerializer(self.reservation).data)

    def test_superuser_cannot_retrieve_non_existent_reservation(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.get('/api/v1/reservations/0/')

        self.assertJSONEqual(response.content, {'detail': 'Not found.'})

    def test_superuser_can_retrieve_all_reservations(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.get('/api/v1/reservations/')

        self.assertJSONEqual(
            response.content,
            ReservationSerializer(Reservation.objects.all(), many=True).data
        )

    def test_user_cannot_update_non_existent_reservation(self):
        url = '/api/v1/reservations/0/'
        response = self.client.post(url, content_type='application/json', data=json.dumps({
            'first_name': self.reservation.first_name,
            'last_name': self.reservation.last_name,
            'address': self.reservation.address,
            'email': self.reservation.email,
            'num_attending': self.reservation.num_attending
        }))

        self.assertJSONEqual(response.content, json.dumps({
            'detail': 'Not found.'
        }))

    @patch('reservations.apis.send_mail')
    def test_updated_reservation_sends_mail(self, mock_send_mail):
        url = '/api/v1/reservations/%d/' % (self.reservation.id,)
        self.client.post(url, content_type='application/json', data=json.dumps({
            'first_name': self.reservation.first_name,
            'last_name': self.reservation.last_name,
            'address': self.reservation.address,
            'email': self.reservation.email,
            'num_attending': self.reservation.num_attending
        }))

        mock_send_mail.assert_called_once_with(
            'Reservation',
            message=WAIT_LIST_MESSAGE,
            from_email='rsvp@rsvpcapitalone.com',
            recipient_list=[self.reservation.email],
            fail_silently=True
        )

    @patch('reservations.apis.send_mail')
    def test_can_create_new_reservation(self, mock_send_mail):
        url = '/api/v1/reservations/'
        response = self.client.post(url, content_type='application/json', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Lennon',
            'address': '456 South Street',
            'email': 'john.lennon@example.com',
            'num_attending': 1
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 2)
        self.assertIsNone(Reservation.objects.last().wait_listed)

    @patch('reservations.apis.MAX_NUM_RESERVATIONS')
    @patch('reservations.apis.send_mail')
    def test_reservation_is_wait_listed_if_max_reservations_reached(
        self,
        mock_send_mail,
        mock_max_num_reservations
    ):
        mock_max_num_reservations.return_value = 1

        url = '/api/v1/reservations/'
        response = self.client.post(url, content_type='application/json', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Lennon',
            'address': '456 South Street',
            'email': 'john.lennon@example.com',
            'num_attending': 1
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 2)
        self.assertFalse(Reservation.objects.last().wait_listed)

    @patch('reservations.apis.send_mail')
    def test_new_reservation_sends_email(self, mock_send_mail):
        url = '/api/v1/reservations/'
        self.client.post(url, content_type='application/json', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Lennon',
            'address': '456 South Street',
            'email': 'john.lennon@example.com',
            'num_attending': 1
        }))

        mock_send_mail.assert_called_once_with(
            'Reservation',
            message=CONFIRMATION_MESSAGE,
            from_email='rsvp@rsvpcapitalone.com',
            recipient_list=['john.lennon@example.com'],
            fail_silently=True
        )