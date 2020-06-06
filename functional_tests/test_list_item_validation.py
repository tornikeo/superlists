from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest
import time

class ItemValidationTest(FunctionalTest):
    def test_cannot_add_empty_list_items(self):
        # Edith goes to home page and accidentally tries to
        # submit an empty input box
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_text').send_keys(Keys.ENTER)

        # The home page refreshes and there is an error message 
        # Saying that list items cannot be blank
        # self.wait_for(lambda: self.assertEqual(
        #     self.browser.find_element_by_css_selector('.has-error').text,
        #     "You can't have an empty list item"
        # ))
        self.wait_for(lambda: self.browser.find_elements_by_css_selector(
            '#id_text:invalid'
        ))

        # She tries again with some text for the item, which now works
        self.browser.find_element_by_id('id_text').send_keys("Buy milk")
        self.browser.find_element_by_id('id_text').send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        # Perversely she now decides to submit a second blank list item
        self.browser.find_element_by_id('id_text').send_keys(Keys.ENTER)

        # She receives a similar warning on the list page
        self.wait_for(lambda: self.browser.find_elements_by_css_selector(
            '#id_text:invalid'
        ))

        # And she can correct it by filling some text in
        self.browser.find_element_by_id('id_text').send_keys("Make tea")
        self.browser.find_element_by_id('id_text').send_keys(Keys.ENTER)

        self.wait_for_row_in_list_table('1: Buy milk')
        self.wait_for_row_in_list_table('2: Make tea')