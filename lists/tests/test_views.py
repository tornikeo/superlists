from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from lists.views import home_page
from django.template.loader import render_to_string
from lists.models import Item, List
from lists.forms import (
    ItemForm, EMPTY_ITEM_ERROR, 
    DUPLICATE_ITEM_ERROR, ExistingListItemForm,
)
from django.utils.html import escape
from unittest import skip

class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)
        
class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        list_ = List.objects.create()
        Item.objects.create(text='Item 1', list=list_)
        Item.objects.create(text='Item 2',list=list_)

        other_list = List.objects.create()
        Item.objects.create(text='Other item 1', list=other_list)
        Item.objects.create(text='Other item 2', list=other_list)

        response = self.client.get(f'/lists/{list_.id}/')
        self.assertContains(response, 'Item 1',)
        self.assertContains(response, 'Item 2',)
        self.assertNotContains(response, 'Other item 1')
        self.assertNotContains(response, 'Other item 2')

    def test_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()
        response = self.client.post(f'/lists/{list_.id}/',
            data={'text':''},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)
    
    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

    def test_uses_correct_template_to_display_lists(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')
    
    def test_for_invalid_input_shows_error_on_page(self):
        list_ = List.objects.create()
        self.client.post(f'/lists/{list_.id}/',
            data={'text':'Buy milk'}
        )
        response = self.client.post(f'/lists/{list_.id}/',
            data={'text':'Buy milk'}
        )
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.count(), 1)
        self.assertContains(response, escape(DUPLICATE_ITEM_ERROR))

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_for_invalid_input_passes_form_to_template(self):
        list_ = List.objects.create()
        response = self.client.post(f'/lists/{list_.id}/',
            data={'text':''}
        )
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

class NewListTest(TestCase):
    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'text':'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new',data={'text':'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post('/lists/new', data={'text':''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )

    def test_invalid_list_items_arent_saved(self):
        response = self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        correct_list = List.objects.create()
        other_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/', 
            data={'text':'New item in existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()

        self.assertEqual(new_item.text, 'New item in existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text':'New item in existing list'},
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

