__author__ = 'parentj@eab.com (Jason Parent)'

# Standard library imports...
import json
from unittest import skip

# Third-party imports...
from mock import Mock, patch

# Django imports...
from django.http import HttpRequest
from django.test import Client, TestCase

# Local imports...
from ..apis import api_reservations, CONFIRMATION_MESSAGE, WAITLIST_MESSAGE
from ..models import Reservation


class ReservationsViewTest(TestCase):
    fixtures = ['reservations']

    def setUp(self):
        self.client = Client()
        self.reservation = Reservation.objects.first()

    def test_non_superuser_cannot_retrieve_reservations(self):
        request = HttpRequest()
        request.user = Mock(is_superuser=False)
        request.method = 'GET'
        response = api_reservations(request)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'You must have superuser privileges to access this information.')

    def test_superuser_can_retrieve_existing_reservation(self):
        request = HttpRequest()
        request.user = Mock(is_superuser=True)
        request.method = 'GET'
        response = api_reservations(request, reservation_id=self.reservation.id)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, self.reservation.to_json())

    def test_superuser_cannot_retrieve_non_existent_reservation(self):
        request = HttpRequest()
        request.user = Mock(is_superuser=True)
        request.method = 'GET'

        with self.assertRaisesMessage(Exception, 'No Reservation matches the given query.'):
            api_reservations(request, reservation_id=2)

    def test_superuser_can_retrieve_all_reservations(self):
        request = HttpRequest()
        request.user = Mock(is_superuser=True)
        request.method = 'GET'
        response = api_reservations(request)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [self.reservation.to_json()])

    @skip('Needs fix...')
    def test_cannot_post_improperly_formatted_data(self):
        response = self.client.post('/api/v1/reservations/', content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '')

    def test_cannot_update_reservation_without_email(self):
        url = '/api/v1/reservations/%d/' % (self.reservation.id,)
        response = self.client.post(url, content_type='application/json', data=json.dumps({
            'first_name': self.reservation.first_name,
            'last_name': self.reservation.last_name,
            'address': self.reservation.address,
            # 'email': self.reservation.email,
            'num_attending': self.reservation.num_attending
        }))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'You must provide the email associated with the reservation ID.')

    def test_cannot_update_non_existent_reservation(self):
        url = '/api/v1/reservations/0/'
        response = self.client.post(url, content_type='application/json', data=json.dumps({
            'first_name': self.reservation.first_name,
            'last_name': self.reservation.last_name,
            'address': self.reservation.address,
            'email': self.reservation.email,
            'num_attending': self.reservation.num_attending
        }))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'A reservation with the given ID and email was not found.')

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
            message=WAITLIST_MESSAGE,
            from_email='rsvp@rsvpcapitalone.com',
            recipient_list=[self.reservation.email],
            fail_silently=True
        )

    def test_cannot_create_reservation_without_parameters(self):
        url = '/api/v1/reservations'
        response = self.client.post(url, content_type='application/json', data=json.dumps({}))

        self.assertEqual(response.status_code, 400)

        expected_message = ''.join([
            'You must provide all of the required parameters: first_name, last_name, address,',
            'email, num_attending.'
        ])

        self.assertEqual(response.content, expected_message)

    @patch('reservations.apis.send_mail')
    def test_can_create_new_reservation(self, mock_send_mail):
        url = '/api/v1/reservations'
        response = self.client.post(url, content_type='application/json', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Lennon',
            'address': '456 South Street',
            'email': 'john.lennon@example.com',
            'num_attending': 1
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 2)
        self.assertIsNone(Reservation.objects.last().waitlisted)

    @patch('reservations.apis.MAX_NUM_RESERVATIONS')
    @patch('reservations.apis.send_mail')
    def test_reservation_is_waitlisted_if_max_reservations_reached(
        self,
        mock_send_mail,
        mock_max_num_reservations
    ):
        mock_max_num_reservations.return_value = 1

        url = '/api/v1/reservations'
        response = self.client.post(url, content_type='application/json', data=json.dumps({
            'first_name': 'John',
            'last_name': 'Lennon',
            'address': '456 South Street',
            'email': 'john.lennon@example.com',
            'num_attending': 1
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 2)
        self.assertFalse(Reservation.objects.last().waitlisted)

    @patch('reservations.apis.send_mail')
    def test_new_reservation_sends_email(self, mock_send_mail):
        url = '/api/v1/reservations'
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