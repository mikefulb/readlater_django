import os
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
    NUM_UNREAD_ARTICLES = 10
    NUM_READ_ARTICLES = 6
    NUM_ARTICLES = NUM_READ_ARTICLES + NUM_UNREAD_ARTICLES
    NUM_CATEGORIES = 5

    # NOTE: if NUM_ARTICLES or NUM_CATEGORIES is changed then this list has to be updated to
    # the resulting article list order using appropriate sorting!
    PRIORITY_SORT_ARGS = [5, 0, 6, 1, 7, 2, 8, 3, 9, 4]
    CATEGORY_SORT_ARGS = [0, 5, 1, 6, 2, 7, 3, 8, 4, 9]
    PROGRESS_SORT_ARGS = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

    def _create_article_list(self):
        for categ_id in range(self.NUM_CATEGORIES):
            Category.objects.create(name=f'Category {categ_id}')

        # skip over the uncategorized category record created in migration
        categ_id = 2
        for article_id in range(self.NUM_ARTICLES):
            art_categ = Category.objects.get(id=categ_id)
            name = f'Article {article_id}'
            notes = f'Note {article_id}'
            priority = self.PRIORITY_LEVELS[article_id % 5]
            progress = (article_id * 10)
            if progress > 100:
                progress = 100
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

            categ_id += 1
            if categ_id == (self.NUM_CATEGORIES + 2):
                categ_id = 2

    def _check_article_list_ordering(self, sort_ordering_args, num_rows_expected):
        tbody = self.selenium.find_element_by_tag_name('tbody')
        rows = tbody.find_elements_by_tag_name('tr')
        self.assertEqual(len(rows), num_rows_expected)

        # loops through rows and use the precomputed list for priority sorting to check list
        # isort is the loop index used to generate rows in _create_article_list() while
        # isort+1 will be the pk of the article created in db since these start at 1 while
        # loop index started at 0
        for i, row in enumerate(rows):
            cols = row.find_elements_by_tag_name('td')
            isort = sort_ordering_args[i]
            progress = (i * 10)
            if progress > 100:
                continue
            self.assertEqual(cols[0].text, 'LINK')
            self.assertEqual(cols[1].text, f'Article {isort}')
            self.assertEqual(cols[2].text, f'Category {isort % self.NUM_CATEGORIES}')
            self.assertEqual(cols[3].text, f'Note {isort}')
            self.assertEqual(cols[4].text, f'{self.PRIORITIES[isort % self.NUM_CATEGORIES]}')
            self.assertEqual(cols[5].text, f'{(isort * 10) % 101}')
            edit_anchor = cols[9].find_element_by_tag_name('a').get_attribute('href')
            expected = urljoin(self.live_server_url, f'/readlater/article/edit/{isort+1}?state=unread')
            self.assertEqual(edit_anchor, expected)
            del_anchor = cols[10].find_element_by_tag_name('a').get_attribute('href')
            expected = urljoin(self.live_server_url, f'/readlater/article/delete/{isort+1}?state=unread')
            self.assertEqual(del_anchor, expected)

    def test_load_article_empty_list(self):
        url = urljoin(self.live_server_url, reverse('article_list'))
        self.selenium.get(url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self.assertIn('There are no articles', self.selenium.page_source)

    def test_load_article_populated_unread_list(self):
        self._create_article_list()
        url = urljoin(self.live_server_url, reverse('article_list'))
        self.selenium.get(url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        # test default is priority sorting
        self._check_article_list_ordering(self.PRIORITY_SORT_ARGS, self.NUM_UNREAD_ARTICLES)

        # click on progress column header to switch to sort by category
        prog_col_header = self.selenium.find_element_by_link_text('Progress')
        self.assertIsNotNone(prog_col_header)
        prog_col_header.click()

        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self._check_article_list_ordering(self.PROGRESS_SORT_ARGS, self.NUM_UNREAD_ARTICLES)


        # click on cateogry column header to switch to sort by category
        cat_col_header = self.selenium.find_element_by_link_text('Category')
        self.assertIsNotNone(cat_col_header)
        cat_col_header.click()

        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self._check_article_list_ordering(self.CATEGORY_SORT_ARGS, self.NUM_UNREAD_ARTICLES)
