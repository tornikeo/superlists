from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from lists.views import home_page
from django.template.loader import render_to_string
from lists.models import Item, List

class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        # Create a new list
        list_ = List()
        list_.save()
        
        # Create list item and add it to list
        first_item = Item()
        first_item.text = 'First Item'
        first_item.list = list_
        first_item.save()

        #Create a second item and add it to list as well
        second_item = Item()
        second_item.text = 'Second Item'
        second_item.list = list_
        second_item.save()
        
        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        saved_lists = List.objects.all()
        self.assertEqual(saved_lists.count(), 1)

        first_saved = saved_items[0]
        saved_second = saved_items[1]
        self.assertEqual(first_saved.text, 'First Item')
        self.assertEqual(saved_second.text, 'Second Item')

        self.assertEqual(first_saved.list, list_)
        self.assertEqual(saved_second.list, list_)
