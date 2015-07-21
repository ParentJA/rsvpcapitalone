__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Django imports...
from django.test import Client, TestCase


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')