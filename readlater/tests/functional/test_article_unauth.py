from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from .utils import FunctionalTestUnauthAccessMixin, FunctionalTestBaseMixin


class ArticleListUnauthTestCase(FunctionalTestUnauthAccessMixin,
                                FunctionalTestBaseMixin, StaticLiveServerTestCase):
    """
    Access several URLs without being logged in and verify redirection to the login
    page.
    """

    def test_unauth_load_article_list(self):
        self._test_unauth_get(reverse('article_list'))

    def test_unauth_create_article_list(self):
        self._test_unauth_get(reverse('article_create_form'))

    def test_unauth_edit_article_list(self):
        self._test_unauth_get(reverse('article_edit_form', kwargs={'pk': 1}))

    def test_unauth_delete_article_list(self):
        self._test_unauth_get(reverse('article_delete_form', kwargs={'pk': 1}))


class ArticleListUnauthPostTestCase(FunctionalTestUnauthAccessMixin,
                                    StaticLiveServerTestCase):
    """
    Send POST requests to URLs without being logged in and verify a 403 (forbidden)
    response.

    Note the 403 occurs because of a CSRF token exception.
    """

    def test_unauth_create_article_post(self):
        self._test_unauth_post(reverse('article_create_form'))

    def test_unauth_edit_article_post(self):
        self._test_unauth_post(reverse('article_edit_form', kwargs={'pk': 1}))

    def test_unauth_delete_article_post(self):
        self._test_unauth_post(reverse('article_delete_form', kwargs={'pk': 1}))
