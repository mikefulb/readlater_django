import logging

from readlater.tests.unit.utils import AssertUnauthRedirectMixin

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)

from django.urls import reverse
from django.test import TestCase


class SettingsViewUnauthTest(AssertUnauthRedirectMixin, TestCase):

    def test_view_url_unauth_redirect(self):
        self.assert_unauth_redirect_url('/readlater/settings/',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('settings'),
                                        template='registration/login.html')


class CategoryCreateNewViewTest(AssertUnauthRedirectMixin, TestCase):

    def test_category_create_view_unauth_redirect(self):
        self.assert_unauth_redirect_url('/readlater/category/create/new',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('category_create_form'),
                                        template='registration/login.html')

    def test_category_create_post_unauth_redirect(self):
        self.assert_unauth_redirect_url(reverse('category_create_form'),
                                        template='registration/login.html')


class CategoryEditViewTest(AssertUnauthRedirectMixin, TestCase):

    def test_category_edit_view_unauth_redirect(self):
        self.assert_unauth_redirect_url('/readlater/category/edit/1',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('category_edit_form', kwargs={'pk': 1}),
                                        template='registration/login.html')

    def test_category_edit_post_unauth_redirect(self):
        self.assert_unauth_redirect_url(reverse('category_edit_form',
                                                kwargs={'pk': 1}),
                                        template='registration/login.html')


class CategoryDeleteViewTest(AssertUnauthRedirectMixin, TestCase):

    def test_category_delete_view_unauth_redirect(self):
        self.assert_unauth_redirect_url('/readlater/category/delete/1',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('category_delete_form', kwargs={'pk': 1}),
                                        template='registration/login.html')

    def test_category_delete_post_unauth_redirect(self):
        self.assert_unauth_redirect_post(reverse('category_delete_form', kwargs={'pk': 1}),
                                         template='registration/login.html')
