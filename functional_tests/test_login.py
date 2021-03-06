from django.core import mail
from selenium.webdriver.common.keys import Keys
import re
from .base import FunctionalTest

TEST_EMAIL = 'test@example.com'
SUBJECT = 'Your login link for Superlists'

class LoginTest(FunctionalTest):
    def test_can_get_email_link_to_log_in(self):
        # User goes to awesome superlists website
        # and notices a "Log in" section in the navbar
        # It says to enter her email address
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('email').send_keys(TEST_EMAIL)
        self.browser.find_element_by_name('email').send_keys(Keys.ENTER)

        # says "check your email to find a message"
        self.wait_for(
            lambda: self.assertIn(
                'Check your email',
                self.browser.find_element_by_tag_name('body').text
            )
        )

        # Check the email
        email = mail.outbox[0]
        self.assertIn(TEST_EMAIL, email.to)
        self.assertEqual(email.subject, SUBJECT)

        # It has a url link in it
        self.assertIn(
            'Use this link to log in',
            email.body
        )
        url_search = re.search(r'http://.+/.+$', email.body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{email.body}')
        url  = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # she clicks on it
        self.browser.get(url)

        # she is logged in
        self.wait_for(
            lambda: self.browser.find_element_by_link_text(
                'Log out'
            )
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(TEST_EMAIL, navbar.text)

        # Now she logs out
        self.browser.find_element_by_link_text('Log out').click()

        # She is logged out
        self.wait_for(
            lambda: self.browser.find_element_by_name('email')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertNotIn(TEST_EMAIL, navbar.text)


        

