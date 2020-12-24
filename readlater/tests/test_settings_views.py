import logging
logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)

from django.urls import reverse
from django.utils.http import urlencode
from django.test import TestCase
from django.db.models import ProtectedError

from ..models import Article, Category


class SettingsViewTest(TestCase):
    NUM_CATEGORIES = 5

    @classmethod
    def setUpTestData(cls):
        for categ_id in range(SettingsViewTest.NUM_CATEGORIES):
            Category.objects.create(name=f'Category {categ_id}')

    def test_settings_url_exists(self):
        response = self.client.get('/readlater/settings/')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<h4>Settings</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('settings'))
        self.assertContains(response, '<h4>Settings</h4>', status_code=200)

    def test_settings_uses_correct_template(self):
        response = self.client.get('/readlater/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/settings_base.html')

    def test_settings_lists_all_categories(self):
        response = self.client.get('/readlater/settings/')
        self.assertEqual(response.status_code, 200)

        # check the number of items in categories list is number created plus one
        # for the uncategorized category created during migration step
        self.assertTrue(len(response.context['category_list']) == SettingsViewTest.NUM_CATEGORIES+1)


class CategoryDeleteViewTest(TestCase):

    @classmethod
    def setUp(self):
        Category.objects.create(name='Category 1')

    def test_category_delete_url_exists(self):
        response = self.client.get('/readlater/category/delete/1')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<h4>Delete Category</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('category_delete_form', kwargs={'pk': 1}))
        self.assertContains(response, '<h4>Delete Category</h4>', status_code=200)

    def test_category_delete_uses_correct_template(self):
        response = self.client.get('/readlater/category/delete/1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/category_delete_form.html')

    def send_delete_post(self, pk, status_code=200):
        url = reverse('category_delete_form', args=(pk,))
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, status_code)
        if response.status_code == 200:
            self.assertRedirects(response, reverse('settings'))

    def test_category_delete_form_valid_post(self):
        """ Test that form properly deletes a record. """
        self.assertEqual(len(Category.objects.all()), 2)
        self.send_delete_post(2)
        self.assertEqual(len(Category.objects.all()), 1)

    def test_category_delete_form_valid_post_protect_pk1(self):
        """ Don't let user delete first record which is Uncategorized. """
        self.assertEqual(len(Category.objects.all()), 2)

        # expect a 403 status code when trying to delete record 1 "Uncategorized"
        self.send_delete_post(1, 403)

        self.assertEqual(len(Category.objects.all()), 2)
