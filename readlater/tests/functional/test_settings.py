import re
from urllib.parse import urljoin

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse


from .utils import FunctionalTestBase
from ...models import Category


class SettingsTestCase(FunctionalTestBase, StaticLiveServerTestCase):

    NUM_CATEGORIES = 10
    MAX_NAME_LEN = 100

    @staticmethod
    def _create_category_name(index):
        return f'Category {index % SettingsTestCase.NUM_CATEGORIES}'

    @staticmethod
    def _get_index_from_category_name(name):
        match = re.match(r'^Category\s(\d*)$', name)
        return int(match.groups()[0])

    def _create_category_list(self):
        # database should be wiped at start of test
        self.assertEqual(len(Category.objects.all()), 0)

        for categ_id in range(self.NUM_CATEGORIES):
            name = self._create_category_name(categ_id)
            Category.objects.create(name=name)

    def _check_category_list_ordering(self, sort_ordering_args, num_rows_expected):
        """
        Using an active webdriver object (self.selenium) search for a table body and
        examine the table rows of the article list.

        :param sort_ordering_args: List of row indices matching sort order, ie. first article is 'Article <n>'
                                   where <n> is the first element of sort_ordering_args, etc.
        :type sort_ordering_args: list
        :param num_rows_expected: Number of rows expected in article list.
        :type num_rows_expected: int
        """
        tbody = self.selenium.find_element_by_tag_name('tbody')
        rows = tbody.find_elements_by_tag_name('tr')
        self.assertEqual(len(rows), num_rows_expected)

        # loops through rows and use the precomputed list for priority sorting to check list
        # isort is the loop index used to generate rows in _create_article_list() while
        # isort+1 will be the pk of the article created in db since these start at 1 while
        # loop index started at 0
        for i, row in enumerate(rows):
            cols = row.find_elements_by_tag_name('td')
            categ_pk = Category.objects.get(name=cols[0].text).id
            isort = sort_ordering_args[i]
            self.assertEqual(cols[0].text, self._create_category_name(isort))
            edit_anchor = cols[1].find_element_by_tag_name('a').get_attribute('href')
            expected = urljoin(self.live_server_url, f'/readlater/category/edit/{categ_pk}')
            self.assertEqual(edit_anchor, expected)
            del_anchor = cols[2].find_element_by_tag_name('a').get_attribute('href')
            expected = urljoin(self.live_server_url, f'/readlater/category/delete/{categ_pk}')
            self.assertEqual(del_anchor, expected)

    def test_load_settings_empty_list(self):
        url = urljoin(self.live_server_url, reverse('settings'))
        self.selenium.get(url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self.assertIn('There are no categories', self.selenium.page_source)

    def test_load_settings_populated_lists(self):
        self._create_category_list()
        url = urljoin(self.live_server_url, reverse('settings'))
        self.selenium.get(url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self._check_category_list_ordering(range(0, self.NUM_CATEGORIES), self.NUM_CATEGORIES)

    def test_load_settings_edit_category(self):
        self._create_category_list()
        url = urljoin(self.live_server_url, reverse('settings'))
        self.selenium.get(url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))

        # find edit link for 1st article and click
        tbody = self.selenium.find_element_by_tag_name('tbody')
        rows = tbody.find_elements_by_tag_name('tr')
        edit_link = rows[0].find_element_by_link_text('EDIT')
        edit_link.click()
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))

        # check fields
        # TODO Need to check order of fields in form as well as just the presence of proper fields
        name_ele = self.selenium.find_element_by_name('name')
        self.assertIsNotNone(name_ele)
        self.assertEqual(name_ele.tag_name, 'input')
        self.assertEqual(name_ele.get_attribute('type'), 'text')
        self.assertEqual(name_ele.get_attribute('maxlength'), f'{self.MAX_NAME_LEN}')

        # parse index in creation list from category name
        categ_name = name_ele.get_attribute('value')
        index = self._get_index_from_category_name(categ_name)
        self.assertEqual(index, 0)

        # change category name and then verify it changed
        name_ele.clear()
        name_ele.send_keys('Astronomy')
        name_ele.submit()

        # wait for form to redirect and load list of categories and verify first category changed
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        tbody = self.selenium.find_element_by_tag_name('tbody')
        rows = tbody.find_elements_by_tag_name('tr')
        cols = rows[0].find_elements_by_tag_name('td')
        self.assertEqual(cols[0].text, 'Astronomy')

    def test_load_settings_create_category(self):
        # verify no categories exist
        self.assertEqual(len(Category.objects.all()), 0)
        url = urljoin(self.live_server_url, reverse('settings'))
        self.selenium.get(url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))

        # find add category link
        create_link = self.selenium.find_element_by_name('create_category_href_bottom')
        create_link.click()
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))

        # check fields
        name_ele = self.selenium.find_element_by_name('name')
        self.assertIsNotNone(name_ele)
        self.assertEqual(name_ele.tag_name, 'input')
        self.assertEqual(name_ele.get_attribute('type'), 'text')
        self.assertEqual(name_ele.get_attribute('maxlength'), f'{self.MAX_NAME_LEN}')

        # enter category and submit
        name_ele.send_keys('Astronomy')
        name_ele.submit()

        # wait for form to redirect and load list of categories and verify first category changed
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        tbody = self.selenium.find_element_by_tag_name('tbody')
        rows = tbody.find_elements_by_tag_name('tr')
        cols = rows[0].find_elements_by_tag_name('td')
        self.assertEqual(cols[0].text, 'Astronomy')
