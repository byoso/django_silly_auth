from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
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

    def test_index_view(self):
        response = self.client.get(reverse('classic_index'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_GET(self):
        response = self.client.get(reverse('classic_login'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_POST(self):
        response = self.client.post(reverse('classic_login'), {'credential': 'testuser', 'password': 'testpass1'})
        self.assertEqual(response.status_code, 302)

    def test_logout_view(self):
        response = self.client.get(reverse('classic_logout'))
        self.assertEqual(response.status_code, 302)

    def test_signup_view_GET(self):
        response = self.client.get(reverse('classic_signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_view_POST(self):
        response = self.client.post(
            reverse('classic_signup'),
            {
                'username': 'test_user_new',
                'email': 'new_user@mail.com',
                'password': 'testpass1',
                'password2': 'testpass1'
            }
            )
        self.assertEqual(response.status_code, 302)

    def test_change_username_GET(self):
        self.authenticate_user()
        response = self.client.get(reverse('classic_change_username'))
        self.assertEqual(response.status_code, 200)

    def test_change_username_POST(self):
        self.authenticate_user()
        response = self.client.post(
            reverse('classic_change_username'), {'username': 'test_user_new_name'})
        self.assertEqual(response.status_code, 302)

    def test_change_email_GET(self):
        self.authenticate_user()
        response = self.client.get(reverse('classic_change_email'))
        self.assertEqual(response.status_code, 200)

    def test_change_email_POST(self):
        self.authenticate_user()
        response = self.client.post(
            reverse('classic_change_email'), {'email': 'new_email@mail.com'})
        self.assertEqual(response.status_code, 302)

    def test_account_view_GET(self):
        self.authenticate_user()
        response = self.client.get(reverse('classic_account'))
        self.assertEqual(response.status_code, 200)

    def test_classic_request_resend_confirmation_email_GET(self):
        response = self.client.get(
            reverse('classic_request_resend_confirmation_email'))
        self.assertEqual(response.status_code, 200)

    def test_request_reset_password_GET(self):
        response = self.client.get(reverse('classic_request_password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_request_reset_password_POST(self):
        response = self.client.post(
            reverse('classic_request_password_reset'), {'credential': 'testuser'})
        self.assertEqual(response.status_code, 200)

    def test_reset_password_GET(self):
        token = self.user.get_jwt_token()
        response = self.client.get(reverse('classic_reset_password', args=[token, ]))
        self.assertEqual(response.status_code, 200)

    def test_reset_password_POST(self):
        self.authenticate_user()
        response = self.client.post(
            reverse('classic_reset_password_authenticated'), {'password': 'testpass1', 'password2': 'testpass1'})
        self.assertEqual(response.status_code, 302)
