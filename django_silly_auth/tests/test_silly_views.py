from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout, authenticate
from django.test.client import RequestFactory


User = get_user_model()


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username='testuser', email='test@test.com')
        self.user.set_password('testpass1')
        self.user.is_confirmed = True
        self.user.is_active = True
        self.user.save()

    def authenticate_user(self):
        self.client.login(username='testuser', password='testpass1')

    def test_dsa_confirm_email(self):
        token = self.user.get_jwt_token()
        response = self.client.get(reverse('dsa_confirm_email', args=[token]))
        self.assertEqual(response.status_code, 200)

    def dsa_password_reset_done(self):
        response = self.client.get(reverse('dsa_password_reset_done'))
        self.assertEqual(response.status_code, 200)
