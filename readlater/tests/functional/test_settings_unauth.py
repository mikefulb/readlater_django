from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from .utils import FunctionalTestUnauthAccessMixin, FunctionalTestBaseMixin

LOGIN_PAGE_TEXT = 'Please login to see this page'


class SettingsUnauthTestCase(FunctionalTestUnauthAccessMixin, FunctionalTestBaseMixin,
                             StaticLiveServerTestCase):
    """
    Access several URLs without being logged in and verify redirection to the login page.
    """

    def test_unauth_load_settings(self):
        self._test_unauth_get(reverse('settings'))

    def test_unauth_create_category_list(self):
        self._test_unauth_get(reverse('category_create_form'))

    def test_unauth_edit_category_list(self):
        self._test_unauth_get(reverse('category_edit_form', kwargs={'pk': 1}))

    def test_unauth_delete_category_list(self):
        self._test_unauth_get(reverse('category_delete_form', kwargs={'pk': 1}))


class SettingsUnauthPostTestCase(FunctionalTestUnauthAccessMixin, StaticLiveServerTestCase):
    """
    Send POST requests to URLs without being logged in and verify a 403 (forbidden) response.

    Note the 403 occurs because of a CSRF token exception.
    """

    def test_unauth_create_category_post(self):
        self._test_unauth_post(reverse('category_create_form'))

    def test_unauth_edit_category_post(self):
        self._test_unauth_post(reverse('category_edit_form', kwargs={'pk': 1}))

    def test_unauth_delete_category_post(self):
        self._test_unauth_post(reverse('category_delete_form', kwargs={'pk': 1}))
