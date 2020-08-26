from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token

User = get_user_model()
email = 'test@test.com'
class AuthenticateTest(TestCase):
    def test_returns_None_if_no_such_token(self):
        user = PasswordlessAuthenticationBackend().authenticate(
            'invalid-token'
        )
        self.assertIsNone(user)

    def test_returns_new_user_with_correct_email_if_token_exists(self):
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(
            token.uid
        )
        self.assertIsNotNone(user)
        new_user = User.objects.get(email=email)
        self.assertEqual(user, new_user)
        
    def test_returns_existing_user_with_correct_email_if_token_exists(self):
        existing_user = User.objects.create(email=email)
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(
            token.uid
        )
        self.assertIsNotNone(user)
        self.assertEqual(user, existing_user)

class GetUserTest(TestCase):
    def test_gets_user_by_email(self):
        user = User.objects.create(email=email)
        other_user = User.objects.create(email='blah@blah.com')
        found_user = PasswordlessAuthenticationBackend().get_user(
            email
        )
        self.assertEqual(found_user, user)

    def test_returns_None_if_no_user_with_that_email(self):
        self.assertIsNone(
            PasswordlessAuthenticationBackend().get_user(
                'invalid@email.com'
            )
        )