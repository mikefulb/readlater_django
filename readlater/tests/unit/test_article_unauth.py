import logging

from readlater.tests.unit.utils import AssertUnauthRedirectMixin

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)

from django.urls import reverse
from django.test import TestCase


class ArticleListViewUnauthTest(AssertUnauthRedirectMixin, TestCase):

    def test_view_url_unauth_redirect(self):
        self.assert_unauth_redirect_url('/readlater/articles/',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url('/readlater/articles/unread',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url('/readlater/articles/read',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('article_list'),
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('article_list_with_state',
                                                args=['unread']),
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('article_list_with_state',
                                                args=['read']),
                                        template='registration/login.html')


class ArticleCreateNewViewTest(AssertUnauthRedirectMixin, TestCase):

    def test_article_create_view_unauth_redirect(self):
        self.assert_unauth_redirect_url('/readlater/article/create/new',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('article_create_form'),
                                        template='registration/login.html')

    def test_article_create_post_unauth_redirect(self):
        self.assert_unauth_redirect_url(reverse('article_create_form'),
                                        template='registration/login.html')


class ArticleEditViewTest(AssertUnauthRedirectMixin, TestCase):

    def test_article_edit_view_unauth_redirect(self):
        self.assert_unauth_redirect_url('/readlater/article/edit/1',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('article_edit_form',
                                                kwargs={'pk': 1}),
                                        template='registration/login.html')

    def test_article_edit_post_unauth_redirect(self):
        self.assert_unauth_redirect_url(reverse('article_edit_form',
                                                kwargs={'pk': 1}),
                                        template='registration/login.html')


class ArticleDeleteViewTest(AssertUnauthRedirectMixin, TestCase):

    def test_article_delete_view_unauth_redirect(self):
        self.assert_unauth_redirect_url('/readlater/article/delete/1',
                                        template='registration/login.html')
        self.assert_unauth_redirect_url(reverse('article_delete_form', kwargs={'pk': 1}),
                                        template='registration/login.html')

    def test_article_delete_post_unauth_redirect(self):
        self.assert_unauth_redirect_post(reverse('article_delete_form', kwargs={'pk': 1}),
                                         template='registration/login.html')
