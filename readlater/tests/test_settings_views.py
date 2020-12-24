import logging
logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)

from django.urls import reverse
from django.utils.http import urlencode
from django.test import TestCase

from ..models import Article, Category
from ..forms import ArticleCreateForm, ArticleEditForm


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
