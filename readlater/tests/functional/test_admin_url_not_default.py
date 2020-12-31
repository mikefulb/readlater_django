import re
import time
import datetime
from urllib.parse import urljoin

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from .utils import FunctionalTestBaseMixin, FunctionalTestLoginMixin

from ...models import Article, Category

PAGE_DELAY_SEC = 0.25


class AdminUrlNotDefaultTest(FunctionalTestBaseMixin, StaticLiveServerTestCase):

    def test_admin_url_not_default(self):
        url = urljoin(self.live_server_url, '/admin/')
        response = self.selenium.get(url)
        time.sleep(PAGE_DELAY_SEC)
        self.wait_for(lambda: self.assertIn('html', self.selenium.page_source))
        self.assertIn('not found', self.selenium.page_source.lower())

        url = urljoin(self.live_server_url, '/admin')
        response = self.selenium.get(url)
        time.sleep(PAGE_DELAY_SEC)
        self.wait_for(lambda: self.assertIn('html', self.selenium.page_source))
        self.assertIn('not found', self.selenium.page_source.lower())
