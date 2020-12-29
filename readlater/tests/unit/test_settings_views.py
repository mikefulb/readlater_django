import logging

from .utils import TestUserMixin

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)

from django.urls import reverse
from django.test import TestCase

from ...models import Category
from ...forms import CategoryCreateForm, CategoryEditForm

MAX_CATEG_LEN = 100


class SettingsViewTest(TestUserMixin, TestCase):
    NUM_CATEGORIES = 5

    @classmethod
    def setUpTestData(cls):
        for categ_id in range(SettingsViewTest.NUM_CATEGORIES):
            Category.objects.create(name=f'Category {categ_id}')

    def test_settings_url_exists(self):
        self._login()
        response = self.client.get('/readlater/settings/')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<h4>Settings</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('settings'))
        self.assertContains(response, '<h4>Settings</h4>', status_code=200)

    def test_settings_uses_correct_template(self):
        self._login()
        response = self.client.get('/readlater/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/settings_base.html')

    def test_settings_lists_all_categories(self):
        self._login()
        response = self.client.get('/readlater/settings/')
        self.assertEqual(response.status_code, 200)

        # check the number of items in categories list is number created plus one
        # for the uncategorized category created during migration step
        self.assertTrue(len(response.context['category_list']) == SettingsViewTest.NUM_CATEGORIES)


class CategoryCreateNewViewTest(TestUserMixin, TestCase):

    def test_category_create_url_exists(self):
        self._login()
        response = self.client.get('/readlater/category/create/new')

        self.assertContains(response, '<h4>Create Category</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('category_create_form'))
        self.assertContains(response, '<h4>Create Category</h4>', status_code=200)

    def test_category_create_uses_correct_template(self):
        self._login()
        response = self.client.get('/readlater/category/create/new')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/category_create_form.html')

    def test_category_create_form_valid_data(self):
        form = CategoryCreateForm({'name': 'Good Category'})
        self.assertTrue(form.is_valid())

    def test_category_create_form_invalid_name_data(self):
        form = CategoryCreateForm({'name': 'A'*(MAX_CATEG_LEN+1)})
        self.assertFalse(form.is_valid())

    def test_category_create_form_valid_post(self):
        self._login()
        self.assertEqual(len(Category.objects.all()), 0)
        response = self.client.post(reverse('category_create_form'),
                                    data={'name': 'Good category'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('settings'))
        self.assertEqual(len(Category.objects.all()), 1)


class CategoryEditViewTest(TestUserMixin, TestCase):

    def setUp(self):
        super().setUp()
        Category.objects.create(name='Category 1')

    def test_category_edit_url_exists(self):
        self._login()
        categ_id = Category.objects.get(name='Category 1').id
        response = self.client.get(f'/readlater/category/edit/{categ_id}')
        self.assertContains(response, '<h4>Edit Category</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('category_edit_form', kwargs={'pk': categ_id}))
        self.assertContains(response, '<h4>Edit Category</h4>', status_code=200)

    def test_category_edit_uses_correct_template(self):
        self._login()
        categ_id = Category.objects.get(name='Category 1').id
        response = self.client.get(f'/readlater/category/edit/{categ_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/category_edit_form.html')

    def test_category_edit_form_valid_data(self):
        form = CategoryEditForm({'name': 'Good Category'})
        self.assertTrue(form.is_valid())

    def test_category_edit_form_invalid_name_data(self):
        form = CategoryEditForm({'name': 'A' * (MAX_CATEG_LEN+1)})
        self.assertFalse(form.is_valid())

    def test_category_edit_form_valid_post(self):
        self._login()
        categ_id = Category.objects.get(name='Category 1').id
        response = self.client.post(reverse('category_edit_form', kwargs={'pk': categ_id}),
                                    data={'name': 'Good category'}, follow=True)
        new_categ = Category.objects.get(id=categ_id)
        self.assertEqual(new_categ.name, 'Good category')
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('settings'))


class CategoryDeleteViewTest(TestUserMixin, TestCase):

    def setUp(self):
        super().setUp()
        Category.objects.create(name='Category 1')

    def test_category_delete_url_exists(self):
        self._login()
        categ_id = Category.objects.get(name='Category 1').id
        response = self.client.get(f'/readlater/category/delete/{categ_id}')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<h4>Delete Category</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('category_delete_form', kwargs={'pk': 1}))
        self.assertContains(response, '<h4>Delete Category</h4>', status_code=200)

    def test_category_delete_uses_correct_template(self):
        self._login()
        categ_id = Category.objects.get(name='Category 1').id
        response = self.client.get(f'/readlater/category/delete/{categ_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/category_delete_form.html')

    def send_delete_post(self, pk, status_code=200):
        self._login()
        url = reverse('category_delete_form', args=(pk,))
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, status_code)
        if response.status_code == 200:
            self.assertRedirects(response, reverse('settings'))

    def test_category_delete_form_valid_post(self):
        """ Test that form properly deletes a record. """
        self.assertEqual(len(Category.objects.all()), 1)
        categ_id = Category.objects.get(name='Category 1').id
        self.send_delete_post(categ_id)
        self.assertEqual(len(Category.objects.all()), 0)

    def test_category_delete_form_valid_post_protect_pk1(self):
        """ Don't let user delete first record which is Uncategorized. """
        # make sure uncategorized category exists
        self._login()
        uncat = Category.get_uncategorized()

        nobjects = len(Category.objects.all())

        # expect a 403 status code when trying to delete record 1 "Uncategorized"
        self.send_delete_post(uncat.id, 403)

        self.assertEqual(len(Category.objects.all()), nobjects)
