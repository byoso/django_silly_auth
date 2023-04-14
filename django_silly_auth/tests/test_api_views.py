
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework .test import APITestCase
from rest_framework.authtoken.models import Token

User = get_user_model()


class TestApiViews(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass1')
        self.user.is_confirmed = True
        self.user.is_active = True
        self.user.save()
        self.token = Token.objects.create(user=self.user)

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def new_user(self):
        user = User.objects.create_user(
            username='new_user', email='new_user@mail.com', password='testpass1')
        user.is_confirmed = True
        user.is_active = True
        user.save()
        return user

    def auth_token(self, user):
        return Token.objects.create(user=user)

    def api_authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.auth_token(user).key)

    def test_login(self):
        url = reverse('token_login')
        response = self.client.post(
            url, {'credential': 'testuser', 'password': 'testpass1'})
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.api_authentication()
        url = reverse('token_logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_email_confirm_email_resend(self):
        self.user.is_confirmed = False
        self.user.save()
        url = reverse('email_confirm_email_resend')
        response = self.client.post(url, {'credential': 'testuserx'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(url, {'credential': 'testuser'})
        self.assertEqual(response.status_code, 200)

    def test_password_request_reset(self):
        url = reverse('password_request_reset')
        response = self.client.post(url, {'credential': 'testuserx'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(url, {'credential': 'testuser'})
        self.assertEqual(response.status_code, 200)

    def test_password_change(self):
        self.api_authentication()
        url = reverse('password_change')
        response = self.client.post(url, {'password': 'testpass1', 'password2': 'testpass1x'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(url, {'password': 'testpass1', 'password2': 'testpass1'})
        self.assertEqual(response.status_code, 200)

    def test_email_request_change(self):
        self.api_authentication()
        url = reverse('email_request_change')
        response = self.client.post(url, {'email': 'new_email@mail.com'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {'email': 'new_email_mail.com'})
        self.assertEqual(response.status_code, 400)

    def test_username_change(self):
        self.api_authentication()
        url = reverse('username_change')
        response = self.client.post(url, {'username': 'new_username'})
        self.assertEqual(response.status_code, 200)

    def test_users_my_infos(self):
        self.api_authentication()
        url = reverse('users_my_infos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_users_delete_me(self):
        self.assertEqual(User.objects.count(), 1)
        self.api_authentication()
        url = reverse('users_delete_me')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)
