import os
import time
from urllib.parse import urljoin

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

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

class FunctionalTest(StaticLiveServerTestCase):

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


class ArticleListTestCase(FunctionalTest):

    def test_load_article_list(self):
        url = urljoin(self.live_server_url, reverse('article_list'))
        self.selenium.get(url)
        breakpoint()
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
