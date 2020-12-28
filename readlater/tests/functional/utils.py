import os
import time

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
