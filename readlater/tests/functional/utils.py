import os
import time

from django.contrib.auth.models import User
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

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
        super().setUp()
        self.selenium = webdriver.Firefox()
        self.selenium.implicitly_wait(10)
        self.staging_server = os.environ.get('STAGING_SERVER')
        if self.staging_server:
            self.live_server_url = self.staging_server

    def tearDown(self):
        super().tearDown()
        #time.sleep(1)
        self.selenium.quit()

    @wait
    def wait_for(self, fn):
        fn()


class FunctionalTestLoginMixin:

    TEST_USERNAME = 'TestUser'
    TEST_EMAIL = 'testuser@example.com'
    TEST_PASSWORD = 'testuserpassword'

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(self.TEST_USERNAME, self.TEST_EMAIL, self.TEST_PASSWORD)

    def tearDown(self):
        super().tearDown()
        self.user.delete()

    def _login(self, login_url, username=TEST_USERNAME, password=TEST_PASSWORD):
        """
        Sends login information and waits for redirected page to load.

        Modified the 'selenium' attribute of object.

        :param login_url: URL for login page.
        :type login_url: str
        :param username: Username for login authentication.
        :type username: str
        :param password: Password for login authentication.
        :type password: str
        """

        # load page
        self.selenium.get(login_url)
        self.wait_for(lambda: self.assertIn('Username', self.selenium.page_source))

        # enter values
        username_ele = self.selenium.find_element_by_name('username')
        self.assertIsNotNone(username_ele)
        username_ele.send_keys(username)

        password_ele = self.selenium.find_element_by_name('password')
        self.assertIsNotNone(password_ele)
        password_ele.send_keys(password)

        # submit
        password_ele.submit()

        # wait for form to redirect and load list of categories and verify first category changed
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
