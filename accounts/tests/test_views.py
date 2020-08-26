from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Token
from accounts import views
from unittest.mock import patch, call
import uuid

User = get_user_model()
email = 'test@testing.com'
token = str(uuid.uuid4())

class SendLoginEmailViewTest(TestCase):
    def test_creates_token_associated_with_email(self):
        response = self.client.post('/accounts/send_login_email', 
            data={'email':email}
        )
        token = Token.objects.first()
        self.assertEqual(token.email, email)

    @patch('accounts.views.send_mail')
    def test_sends_mail_to_address_from_post(self, mock_send_mail):
        self.client.post('/accounts/send_login_email', data={
            'email': email
        })
        self.assertTrue(mock_send_mail.called, True)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Superlists')
        self.assertEqual(from_email, 'noreply@superlists.xyz')
        self.assertEqual(to_list, [email])
        
        token = Token.objects.first()
        self.assertIn(token.uid, body)

    def test_adds_success_message(self):
        response = self.client.post('/accounts/send_login_email',
            data={
                'email':email
            }, 
            follow=True,
        )
        message = list(response.context['messages'])[0]
        self.assertEqual(
            message.message,
            "Check your email, we've sent you a link you can use to log in."
        )

@patch('accounts.views.auth')
class LoginViewTest(TestCase):
    def test_redirects_to_home_page(self, mock_auth):
        response = self.client.get('/accounts/login?token=abcd123')
        self.assertRedirects(response, '/')

    def test_calls_authenticate_with_uid_from_get_request(self, mock_auth):
        token = uuid.uuid4()
        self.client.get(f'/accounts/login?token={token}')
        self.assertEqual(
            mock_auth.authenticate.call_args,
            call(uid=str(token))
        )

    def test_calls_auth_login_with_user_if_there_is_one(self, mock_auth):
        token = uuid.uuid4()
        response = self.client.get(f'/accounts/login?token={token}')
        self.assertEqual(
            mock_auth.login.call_args,
            call(response.wsgi_request, mock_auth.authenticate.return_value)
        )

    def test_does_not_login_if_user_is_not_authenticated(self, mock_auth):
        mock_auth.authenticate.return_value = None
        self.client.get(f'/accounts/login?token={token}')
        self.assertEqual(mock_auth.login.called, False)

@patch('accounts.views.auth')
class LogoutViewTest(TestCase):
    def test_redirects_to_home_page(self, mock_auth):
        response = self.client.get('/accounts/logout')
        self.assertRedirects(response, '/')

    def test_calls_logout_with_request(self, mock_auth):
        self.client.get('/accounts/logout')
        self.assertTrue(mock_auth.logout.called)