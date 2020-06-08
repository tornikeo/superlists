from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from lists.views import home_page
from django.template.loader import render_to_string
from lists.models import Item, List
from django.core.exceptions import ValidationError

class ItemModelTest(TestCase):
    def test_default_text(self):
        item = Item()
        self.assertEqual(item.text, '')

    def test_item_is_related_to_list(self):
        list_ = List.objects.create()
        item = Item()
        item.list = list_
        item.save()
        self.assertEqual([item], list(list_.item_set.all()))

    def test_cannot_save_empty_items(self):
        list_ = List.objects.create()
        item = Item(list=list_, text='')
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_duplicate_items_are_invalid(self):
        list_ = List.objects.create()
        item1 = Item.objects.create(text="Buy milk", list=list_)
        with self.assertRaises(ValidationError):
            item2 = Item(text="Buy milk", list=list_)
            item2.full_clean()
    
    def test_can_save_same_items_to_different_lists(self):
        list1 = List.objects.create()
        list2 = List.objects.create()
        item1 = Item.objects.create(text="Buy milk", list=list1)
        item2 = Item.objects.create(text="Buy milk", list=list2)
        item1.full_clean() #should not rise validation error

    def test_list_ordering(self):
        list1 = List.objects.create()
        items = [Item.objects.create(list=list1, text=str(i)) 
            for i in range(5)
        ]
        self.assertEqual(
            list(Item.objects.all()),
            items,
        )

    def test_string_representation(self):
        item = Item(text='some text')
        self.assertIn('some text', str(item))
        
class ListModelTest(TestCase):
    def test_get_absolute_url(self):
        list_ = List.objects.create()
        self.assertEqual(list_.get_absolute_url(), f'/lists/{list_.id}/')
