import os
import time
from urllib.parse import urljoin

import requests
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10


def get_login_redirect_url(url):
    """
    Create login redirect URL for given url.

    :param url: Target URL.
    :type url: str
    :return: Redirected login URL.
    :rtype: str
    """
    return f'/readlater/accounts/login/?next={url}'


def wait(fn):
    """
    Decorator to wait for selenium function to successfully complete.

    The global MAX_WAIT sets the timeout period in seconds.

    :param fn: Function to try until successful or timeout.
    :type fn: function
    :return: Wrapped function.
    :rtype: function
    """

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


class FunctionalTestBaseMixin:
    """
    Mixin which handles creating an object attribute 'selenium' which is a webdriver
    for the proper browser driver as well as 'staging_server' which is the live test
    server info.

    Intended to be used with the LiveServerTestCase and StaticLiveServerTestCase.
    """

    def setUp(self):
        super().setUp()
        driver = os.environ.get('SELENIUM_DRIVER', 'firefox')
        if driver.lower() == 'firefox':
            self.selenium = webdriver.Firefox()
        elif driver.lower() == 'chrome':
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            self.selenium = webdriver.Chrome(
                executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                chrome_options=chrome_options)
        else:
            raise ValueError(f'Unknown SELINIUM driver {driver} requested!')
        self.selenium.implicitly_wait(10)
        self.staging_server = os.environ.get('STAGING_SERVER')
        if self.staging_server:
            self.live_server_url = self.staging_server

    def tearDown(self):
        super().tearDown()
        self.selenium.quit()

    @wait
    def wait_for(self, fn):
        """
        Wait on selenium function to complete.

        Usage:
           self.wait_for(lambda: self.assertIn('Hello', self.selenium.page_source))

        :param fn: Function to wait on.
        :type fn: func
        """
        fn()


class FunctionalTestLoginMixin:
    """
    Mixin which handles creating a test user and provides a method for loggining
    in using the test user.

    Intended to be used with the LiveServerTestCase and StaticLiveServerTestCase.
    """
    TEST_USERNAME = 'TestUser'
    TEST_EMAIL = 'testuser@example.com'
    TEST_PASSWORD = 'testuserpassword'

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(self.TEST_USERNAME, self.TEST_EMAIL,
                                             self.TEST_PASSWORD)

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

        # wait for form to redirect and load list of categories and verify first
        # category changed
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))


class FunctionalTestUnauthAccessMixin:
    """
    Mixin which handles making GET and POST requests to the test server without being
    logged in and testing the proper redirect or forbidden response is generated.

    Intended to be used with the LiveServerTestCase and StaticLiveServerTestCase.
    """

    LOGIN_PAGE_TEXT = 'Please login to see this page'

    def _test_unauth_get(self, url):
        """
        Try a GET request via selenium and verify redirection to the login page.

        The live test server ip/port information will be added to the URL.

        :param url: Target URL without host ip/port information.
        :type url: str

        """
        get_url = urljoin(self.live_server_url, url)
        self.selenium.get(get_url)
        self.wait_for(lambda: self.assertIn('ReadLater', self.selenium.page_source))
        # seems to help test not hang
        time.sleep(0.25)
        redirect_url = urljoin(self.live_server_url, get_login_redirect_url(url))
        self.assertEqual(redirect_url, self.selenium.current_url)
        self.assertIn(self.LOGIN_PAGE_TEXT, self.selenium.page_source)

    def _test_unauth_post(self, url, data=None):
        """
        Try a POST request via requests package and verify a 403 (forbidden) response.

        The live test server ip/port information will be added to the URL.

        :param url: Target URL without host ip/port information.
        :type url: str
        :param data: Optional data for POST request.
        :type data: dict
        """
        get_url = urljoin(self.live_server_url, url)
        response = requests.post(get_url, data=data)
        self.assertEqual(response.status_code, 403)
