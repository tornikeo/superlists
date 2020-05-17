from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from lists.views import home_page
from django.template.loader import render_to_string
from lists.models import Item, List


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

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

class NewListTest(TestCase):
    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new',data={'item_text':'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'item_text':'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

    def test_uses_correct_template_to_display_lists(self):
        list_ = List.objects.create()

        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        correct_list = List.objects.create()
        other_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/add_item', 
            data={'item_text':'New item in existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()

        self.assertEqual(new_item.text, 'New item in existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/add_item',
            data={'item_text':'New item in existing list'},
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

