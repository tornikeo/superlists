from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib import auth
from accounts.models import Token

User = get_user_model()
email = 'test@testing.com'


class UserModelTestcase(TestCase):
    def test_user_is_valid_with_email_only(self):
        user = User(email=email)
        user.full_clean()
    
    def test_email_is_primary_key(self):
        user = User(email=email)
        self.assertEqual(user.pk,email)

    def test_links_user_with_auto_generated_uid(self):
        token1 = Token.objects.create(email=email)
        token2 = Token.objects.create(email=email)
        self.assertNotEqual(token1.uid, token2.uid)
    
    def test_no_problem_with_auth_login(self):
        user = User.objects.create(email=email)
        user.backend = ''
        request = self.client.request().wsgi_request
        auth.login(request, user) #should not raise