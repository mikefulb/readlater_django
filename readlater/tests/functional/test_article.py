import os
import re
import time
import datetime
from urllib.parse import urljoin

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from ...models import Article, Category

MAX_WAIT = 10


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
    return modified_fn


class FunctionalTestBase:

    def setUp(self):
        self.selenium = webdriver.Firefox()
        self.selenium.implicitly_wait(10)
        self.staging_server = os.environ.get('STAGING_SERVER')
        if self.staging_server:
            self.live_server_url = self.staging_server

    def tearDown(self):
        time.sleep(1)
        self.selenium.quit()
        super().tearDown()

    @wait
    def wait_for(self, fn):
        fn()


class ArticleListTestCase(FunctionalTestBase, StaticLiveServerTestCase):

    PRIORITIES = ['Higher', 'High', 'Normal', 'Low', 'Lower']
    PRIORITY_LEVELS = [0, 100, 200, 300, 400]

    # NOTE: if either of these are changed must also update PRIORITY_SORT_ARGS et al!
    # Also must update _create_article_list as it has hard coded constants to make progress,etc work!
    # So don't change unless you plan on recreating all test data
    # TODO Generate all test data based on these values automatically
    NUM_UNREAD_ARTICLES = 10
    NUM_READ_ARTICLES = 6
    NUM_ARTICLES = NUM_READ_ARTICLES + NUM_UNREAD_ARTICLES
    NUM_CATEGORIES = 5

    # NOTE: if NUM_ARTICLES or NUM_CATEGORIES is changed then this list has to be updated to
    # the resulting article list order using appropriate sorting!
    UNREAD_PRIORITY_SORT_ARGS = [5, 0, 6, 1, 7, 2, 8, 3, 9, 4]
    UNREAD_CATEGORY_SORT_ARGS = [0, 5, 1, 6, 2, 7, 3, 8, 4, 9]
    UNREAD_PROGRESS_SORT_ARGS = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    READ_PRIORITY_SORT_ARGS = [10, 15, 11, 12, 13, 14]
    READ_CATEGORY_SORT_ARGS = [10, 15, 11, 12, 13, 14]
    READ_PROGRESS_SORT_ARGS = [10, 15, 11, 12, 13, 14]

    # TODO Need to make functions for generating record values (article, note, etc) from the
    #      pk in the database so it is algorithmically possible to generate a record
    #      given a pk and also find the pk given a record.  Currently everything is hard
    #      coded or duplicated so maintenance would be more difficult than it should be.

    MAX_NAME_LEN = 100
    MAX_NOTES_LEN = 100
    MAX_URL_LEN = 400

    @staticmethod
    def _create_article_name(index):
        return f'Article {index}'

    @staticmethod
    def _get_index_from_article_name(name):
        match = re.match(r'^Article\s(\d*)$', name)
        return int(match.groups()[0])

    @staticmethod
    def _create_article_category(index):
        return f'Category {index % ArticleListTestCase.NUM_CATEGORIES}'

    @staticmethod
    def _create_article_notes(index):
        return f'Note {index}'

    @staticmethod
    def _create_article_priority_level(index):
        return ArticleListTestCase.PRIORITY_LEVELS[index % len(ArticleListTestCase.PRIORITY_LEVELS)]

    @staticmethod
    def _create_article_priority_name(index):
        return ArticleListTestCase.PRIORITIES[index % len(ArticleListTestCase.PRIORITY_LEVELS)]

    @staticmethod
    def _create_article_progress(index):
        if index < ArticleListTestCase.NUM_UNREAD_ARTICLES:
            progress = (index * 100) // ArticleListTestCase.NUM_UNREAD_ARTICLES
        else:
            progress = 100
        return progress

    def _create_article_list(self):
        # database should be wiped at start of test
        self.assertEqual(len(Article.objects.all()), 0)

        for article_id in range(self.NUM_ARTICLES):
            name = self._create_article_name(article_id)
            notes = self._create_article_notes(article_id)
            categ = self._create_article_category(article_id)
            priority = self._create_article_priority_level(article_id)
            progress = self._create_article_progress(article_id)
            art_categ, _ = Category.objects.get_or_create(name=categ)
            updated = None
            finish = None
            if progress > 0:
                updated = datetime.datetime.now(tz=datetime.timezone.utc)
                if progress == 100:
                    finish = updated
            Article.objects.create(name=name,
                                   notes=notes,
                                   category=art_categ,
                                   priority=priority,
                                   progress=progress,
                                   updated_time=updated,
                                   finished_time=finish)

    def _check_article_list_ordering(self, sort_ordering_args, num_rows_expected, state):
        """
        Using an active webdriver object (self.selenium) search for a table body and
        examine the table rows of the article list.

        :param sort_ordering_args: List of row indices matching sort order, ie. first article is 'Article <n>'
                                   where <n> is the first element of sort_ordering_args, etc.
        :type sort_ordering_args: list
        :param num_rows_expected: Number of rows expected in article list.
        :type num_rows_expected: int
        :param state: Type of article list - 'unread' or 'read'.
        :type state: str
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

            index = self._get_index_from_article_name(cols[1].text)
            art_pk = Article.objects.get(name=cols[1].text).id
            isort = sort_ordering_args[i]
            if state == 'unread':
                offset = 0
            else:
                offset = self.NUM_UNREAD_ARTICLES

            progress = self._create_article_progress(index+offset)
            categ = self._create_article_category(index+offset)
            notes = self._create_article_notes(index)
            priority = self._create_article_priority_name(index+offset)

            self.assertEqual(cols[0].text, 'LINK')
            self.assertEqual(cols[1].text, f'Article {isort}')
            self.assertEqual(cols[2].text, categ)
            self.assertEqual(cols[3].text, notes)
            self.assertEqual(cols[4].text, priority)
            self.assertEqual(cols[5].text, f'{progress}')
            edit_anchor = cols[9].find_element_by_tag_name('a').get_attribute('href')
            expected = urljoin(self.live_server_url, f'/readlater/article/edit/{art_pk}?state={state}')
            self.assertEqual(edit_anchor, expected)
            del_anchor = cols[10].find_element_by_tag_name('a').get_attribute('href')
            expected = urljoin(self.live_server_url, f'/readlater/article/delete/{art_pk}?state={state}')
            self.assertEqual(del_anchor, expected)

    def test_load_article_empty_list(self):
        url = urljoin(self.live_server_url, reverse('article_list'))
        self.selenium.get(url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self.assertIn('There are no articles', self.selenium.page_source)

    def test_load_article_populated_lists(self):
        self._create_article_list()
        url = urljoin(self.live_server_url, reverse('article_list'))
        self.selenium.get(url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))

        # test default is priority sorting
        self._check_article_list_ordering(self.UNREAD_PRIORITY_SORT_ARGS, self.NUM_UNREAD_ARTICLES, 'unread')

        # click on progress column header to switch to sort by category
        prog_col_header = self.selenium.find_element_by_link_text('Progress')
        self.assertIsNotNone(prog_col_header)
        prog_col_header.click()
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self._check_article_list_ordering(self.UNREAD_PROGRESS_SORT_ARGS, self.NUM_UNREAD_ARTICLES, 'unread')

        # click on cateogry column header to switch to sort by category
        cat_col_header = self.selenium.find_element_by_link_text('Category')
        self.assertIsNotNone(cat_col_header)
        cat_col_header.click()
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self._check_article_list_ordering(self.UNREAD_CATEGORY_SORT_ARGS, self.NUM_UNREAD_ARTICLES, 'unread')

        # switch to read articles
        read_anchor = self.selenium.find_element_by_link_text('Read')
        self.assertIsNotNone(read_anchor)
        read_anchor.click()
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self._check_article_list_ordering(self.READ_PRIORITY_SORT_ARGS, self.NUM_READ_ARTICLES, 'read')

        # click on progress column header to switch to sort by category
        prog_col_header = self.selenium.find_element_by_link_text('Progress')
        self.assertIsNotNone(prog_col_header)
        prog_col_header.click()
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self._check_article_list_ordering(self.READ_PROGRESS_SORT_ARGS, self.NUM_READ_ARTICLES, 'read')

        # click on cateogry column header to switch to sort by category
        cat_col_header = self.selenium.find_element_by_link_text('Category')
        self.assertIsNotNone(cat_col_header)
        cat_col_header.click()
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self._check_article_list_ordering(self.READ_CATEGORY_SORT_ARGS, self.NUM_READ_ARTICLES, 'read')

    def test_load_article_edit_article(self):
        self._create_article_list()
        url = urljoin(self.live_server_url, reverse('article_list'))
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

        # parse index in creation list from article name
        # FIXME need more robust way to parse number
        art_name = name_ele.get_attribute('value')
        self.assertIn('Article', art_name)
        index = int(art_name[7:])
        self.assertTrue(isinstance(index, int))

        # self.assertEqual(cols[0].text, 'LINK')
        # self.assertEqual(cols[1].text, f'Article {isort}')
        # self.assertEqual(cols[2].text, )
        # self.assertEqual(cols[3].text, f'Note {isort}')
        # self.assertEqual(cols[4].text, f'{self.PRIORITIES[isort % self.NUM_CATEGORIES]}')
        # self.assertEqual(cols[5].text, f'{progress}')  # f'{(isort * 10) % 101}')
        # FIXME Test values for form element values should come from
        #       a common function instead of these duplicated equations
        url_ele = self.selenium.find_element_by_name('url')
        self.assertIsNotNone(url_ele)
        self.assertEqual(url_ele.tag_name, 'input')
        self.assertEqual(url_ele.get_attribute('type'), 'url')
        self.assertEqual(url_ele.get_attribute('maxlength'), f'{self.MAX_URL_LEN}')

        cat_ele = self.selenium.find_element_by_name('category')
        self.assertIsNotNone(cat_ele)
        self.assertEqual(cat_ele.tag_name, 'select')
        option_eles = cat_ele.find_elements_by_tag_name('option')
        #selected = [i for i, x in enumerate(option_eles) if x.get_attribute('selected') is not None]
        selected = next(filter(None, (i for i, x in enumerate(option_eles) if x.get_attribute('selected') is not None)))
        self.assertEqual(f'Category {index % self.NUM_CATEGORIES}', option_eles[selected].text)

        # test number of categories offered - including the '------'
        # option in additon to NUM_CATEGORIES created in _create_article_list()
        self.assertEqual(len(option_eles), self.NUM_CATEGORIES+1)

        pri_ele = self.selenium.find_element_by_name('priority')
        self.assertIsNotNone(pri_ele)
        self.assertEqual(pri_ele.tag_name, 'select')
        option_eles = pri_ele.find_elements_by_tag_name('option')

        # test number of categories offered - including the '------'
        # and 'Uncategories' options in additon to NUM_CATEGORIES
        # created in _create_article_list()
        self.assertEqual(len(option_eles),  len(self.PRIORITIES))

        prog_ele = self.selenium.find_element_by_name('progress')
        self.assertIsNotNone(prog_ele)
        self.assertEqual(prog_ele.tag_name, 'input')
        self.assertEqual(prog_ele.get_attribute('type'), 'number')

        notes_ele = self.selenium.find_element_by_name('notes')
        self.assertIsNotNone(notes_ele)
        self.assertEqual(notes_ele.tag_name, 'input')
        self.assertEqual(notes_ele.get_attribute('type'), 'text')
        self.assertEqual(notes_ele.get_attribute('maxlength'), f'{self.MAX_NOTES_LEN}')
