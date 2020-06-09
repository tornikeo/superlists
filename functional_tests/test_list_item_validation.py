from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest
import time

class ItemValidationTest(FunctionalTest):
    def get_error_element(self):
        return self.browser.find_element_by_css_selector('.has-error')

    def test_cannot_add_empty_list_items(self):
        # Edith goes to home page and accidentally tries to
        # submit an empty input box
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys(Keys.ENTER)

        # The home page refreshes and there is an error message 
        # Saying that list items cannot be blank
        self.wait_for(lambda: self.browser.find_elements_by_css_selector(
            '#id_text:invalid'
        ))

        # She tries again with some text for the item, which now works
        self.get_item_input_box().send_keys("Buy milk")
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        # Perversely she now decides to submit a second blank list item
        self.get_item_input_box().send_keys(Keys.ENTER)

        # She receives a similar warning on the list page
        self.wait_for(lambda: self.browser.find_elements_by_css_selector(
            '#id_text:invalid'
        ))

        # And she can correct it by filling some text in
        self.get_item_input_box().send_keys("Make tea")
        self.get_item_input_box().send_keys(Keys.ENTER)

        self.wait_for_row_in_list_table('1: Buy milk')
        self.wait_for_row_in_list_table('2: Make tea')

    def test_cannot_add_duplicate_items(self):
        # Edith goes to home page and starts a new list
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys("Buy milk")
        self.get_item_input_box().send_keys(Keys.ENTER)
        
        # The list is correctly diplayed
        self.wait_for_row_in_list_table('1: Buy milk')

        # She tries entering a duplicate
        self.get_item_input_box().send_keys("Buy milk")
        self.get_item_input_box().send_keys(Keys.ENTER)
        

        # The home page refreshes and there is an error message 
        # Saying that list items cannot duplicates
        self.wait_for(lambda: self.assertEqual(
            self.get_error_element().text,
            "You've already got this in your list",
        ))

    def test_errors_are_cleared_on_input(self):
        #Edith starts a new list
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys("Buy milk")
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')
        # Enters a duplicate
        self.get_item_input_box().send_keys("Buy milk")
        self.get_item_input_box().send_keys(Keys.ENTER)
        # duplication error comes up
        self.wait_for(lambda: self.assertTrue(
            self.get_error_element().is_displayed(),
        ))
        # She starts typing
        self.get_item_input_box().send_keys("C")
        # The error message immediately dissapears
        self.wait_for(lambda: self.assertFalse(
            self.get_error_element().is_displayed(),
        ))


