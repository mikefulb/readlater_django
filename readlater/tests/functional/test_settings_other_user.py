import re
import time
from urllib.parse import urljoin

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse


from .utils import FunctionalTestBaseMixin, FunctionalTestLoginMixin
from ...models import Category

# delay used after login which seems to help reliability (not sure why...)
LOGIN_DELAY_SEC = 0.25


class SettingsOtherUserTestCase(FunctionalTestLoginMixin, FunctionalTestBaseMixin,
                       StaticLiveServerTestCase):

    def setUp(self):
        super().setUp()

        Category.objects.create(name='Category Primary User', created_by=self.user)
        Category.objects.create(name='Category Other User', created_by=self.user_other)

    def test_load_settings_other_list(self):
        """
        Verify when logged in as 'other user' we don't see records for the primary user.
        """
        self._login(urljoin(self.live_server_url, reverse('login')), user='other')
        # seems to help to have a delay between login and next page access
        time.sleep(LOGIN_DELAY_SEC)
        url = urljoin(self.live_server_url, reverse('settings'))
        self.selenium.get(url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        self.assertIn('Category Other User', self.selenium.page_source)
        self.assertNotIn('Category Primary User', self.selenium.page_source)
