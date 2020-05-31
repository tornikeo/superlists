from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest

MAX_WAIT = 5

class LayoutAndStylingTest(FunctionalTest):
    def test_layout_and_styling(self):
        # Edith goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10,
        )
        inputbox.send_keys("Testing")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Testing")
        inputbox = self.browser.find_element_by_id("id_new_item")
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size['width'] / 2,
            512,
            delta=10,
        )
