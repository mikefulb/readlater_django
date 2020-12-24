import logging
logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)

from django.urls import reverse
from django.utils.http import urlencode
from django.test import TestCase

from ..models import Article, Category
from ..forms import ArticleCreateForm, ArticleEditForm


class ArticleListViewTest(TestCase):
    NUM_ARTICLES = 10
    NUM_CATEGORIES = 5

    @classmethod
    def setUpTestData(cls):
        for categ_id in range(ArticleListViewTest.NUM_CATEGORIES):
            Category.objects.create(name=f'Category {categ_id}')

        # skip over the uncategorized category record created in migration
        categ_id = 2
        for article_id in range(ArticleListViewTest.NUM_ARTICLES):
            art_categ = Category.objects.get(id=categ_id)
            Article.objects.create(name=f'Article {article_id}',
                                   category=art_categ,
                                   priority=article_id*100,
                                   progress=article_id*10)
            categ_id += 1
            if categ_id == (ArticleListViewTest.NUM_CATEGORIES + 2):
                categ_id = 2

    def test_view_url_exists(self):
        # FIXME need to add some finished articles and verify only those
        #       are visible
        #
        # NOTE Should leverage tests from test_view_unread_url_exists()
        #      as it is the same case

        response = self.client.get('/readlater/articles/')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<a href="read">Read</a>', status_code=200)

        # also test using name
        response = self.client.get(reverse('article_list'))
        self.assertContains(response, '<a href="read">Read</a>', status_code=200)

    def test_view_unread_url_exists(self):
        # FIXME need to add some finished articles and verify only those
        #       are visible
        response = self.client.get('/readlater/articles/unread')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<a href="read">Read</a>', status_code=200)

        # also test using name
        response = self.client.get(reverse('article_list_with_state', args=['unread']))
        self.assertContains(response, '<a href="read">Read</a>', status_code=200)

    def test_view_read_url_exists(self):
        # FIXME need to add some finished articles and verify only those
        #       are visible

        response = self.client.get('/readlater/articles/read')

        # test that 'Unread' is a link to the unread page from the read page
        self.assertContains(response, '<a href="unread">Unread</a>', status_code=200)

        # also test using name
        response = self.client.get(reverse('article_list_with_state', args=['read']))
        self.assertContains(response, '<a href="unread">Unread</a>', status_code=200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/readlater/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/article_list.html')

    def test_view_lists_all_articles(self):
        response = self.client.get('/readlater/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['article_list']) == ArticleListViewTest.NUM_ARTICLES)


class ArticleCreateNewViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name=f'Category {1}')

        # skip over the uncategorized category record created in migration
        categ = Category.objects.get(id=2)
        Article.objects.create(name=f'Article 1',
                               category=categ,
                               priority=200,
                               progress=10)

    def test_article_create_edit_url_exists(self):
        response = self.client.get('/readlater/article/create/new')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<h4>Create Article</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('article_create_form'))
        self.assertContains(response, '<h4>Create Article</h4>', status_code=200)

    def test_article_create_edit_uses_correct_template(self):
        response = self.client.get('/readlater/article/create/new')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/article_create_form.html')

    def test_article_create_form_valid_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleCreateForm(dict(name='Article',
                                      notes='Note',
                                      url='http://this.is.url.org',
                                      category=categ,
                                      priority=0))
        self.assertTrue(form.is_valid())

    def test_article_create_form_invalid_name_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleCreateForm(dict(name='A'*101,
                                      notes='Note',
                                      url='http://this.is.url.org',
                                      category=categ,
                                      priority=0))
        self.assertFalse(form.is_valid())

    def test_article_create_form_invalid_notes_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleCreateForm(dict(name='A'*100,
                                      notes='N'*101,
                                      url='http://this.is.url.org',
                                      category=categ,
                                      priority=0))
        self.assertFalse(form.is_valid())


    def test_article_create_form_invalid_url_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleCreateForm(dict(name='A' * 100,
                                      notes='N' * 100,
                                      url='this is not a url',
                                      category=categ,
                                      priority=0))
        self.assertFalse(form.is_valid())

    def test_article_create_form_invalid_priority_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleCreateForm(dict(name='A' * 100,
                                      notes='N' * 100,
                                      url='http://this.is.url.org',
                                      category=categ,
                                      priority=-1000))
        self.assertFalse(form.is_valid())

    def test_article_create_form_valid_post(self):
        response = self.client.post(reverse('article_create_form'),
                                    data={'name': 'Article',
                                            'notes': 'Notes',
                                            'url': 'http://this.org/index.html',
                                            'category': 1,
                                            'priority': 200,
                                            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('article_list'))


class ArticleEditViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name=f'Category {1}')

        # skip over the uncategorized category record created in migration
        categ = Category.objects.get(id=2)
        Article.objects.create(name=f'Article 1',
                               category=categ,
                               priority=200,
                               progress=10)

    def test_article_edit_url_exists(self):
        response = self.client.get('/readlater/article/edit/1')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<h4>Edit Article</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('article_edit_form', kwargs={'pk': 1}))
        self.assertContains(response, '<h4>Edit Article</h4>', status_code=200)

    def test_article_edit_uses_correct_template(self):
        response = self.client.get('/readlater/article/edit/1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/article_edit_form.html')

    def test_article_edit_form_valid_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleEditForm(dict(name='Article',
                                    notes='Note',
                                    url='http://this.is.url.org',
                                    category=categ,
                                    priority=0,
                                    progress=50))
        self.assertTrue(form.is_valid())

    def test_article_edit_form_invalid_name_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleEditForm(dict(name='A'*101,
                                      notes='Note',
                                      url='http://this.is.url.org',
                                      category=categ,
                                      priority=0,
                                      progress=50))
        self.assertFalse(form.is_valid())

    def test_article_edit_form_invalid_notes_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleEditForm(dict(name='A'*100,
                                      notes='N'*101,
                                      url='http://this.is.url.org',
                                      category=categ,
                                      priority=0,
                                      progress=50))
        self.assertFalse(form.is_valid())

    def test_article_edit_form_invalid_url_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleEditForm(dict(name='A' * 100,
                                      notes='N' * 100,
                                      url='this is not a url',
                                      category=categ,
                                      priority=0,
                                      progress=50))
        self.assertFalse(form.is_valid())

    def test_article_edit_form_invalid_priority_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleEditForm(dict(name='A' * 100,
                                      notes='N' * 100,
                                      url='http://this.is.url.org',
                                      category=categ,
                                      priority=-1000,
                                      progress=50))
        self.assertFalse(form.is_valid())

    def test_article_edit_form_invalid_progress_data(self):
        categ = Category.objects.get(id=1)
        form = ArticleEditForm(dict(name='A' * 100,
                                      notes='N' * 100,
                                      url='http://this.is.url.org',
                                      category=categ,
                                      priority=200,
                                      progress=-500))
        self.assertFalse(form.is_valid())

        form = ArticleEditForm(dict(name='A' * 100,
                                    notes='N' * 100,
                                    url='http://this.is.url.org',
                                    category=categ,
                                    priority=200,
                                    progress=500))
        self.assertFalse(form.is_valid())

    def test_article_edit_form_valid_post(self):
        for state in ['unread', 'read']:
            url = reverse('article_edit_form', args=(1,))
            response = self.client.post(url + '?' + urlencode({'state': state}),
                                        data={'name': 'Article',
                                              'notes': 'Notes',
                                              'url': 'http://this.org/index.html',
                                              'category': 1,
                                              'priority': 200,
                                              'progress': 50
                                              }, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertRedirects(response, reverse('article_list_with_state', args=(state,)))


class ArticleDeleteViewTest(TestCase):

    @classmethod
    def setUp(cls):
        Category.objects.create(name=f'Category {1}')

        # skip over the uncategorized category record created in migration
        categ = Category.objects.get(id=2)
        Article.objects.create(name=f'Article 1',
                               category=categ,
                               priority=200,
                               progress=10)

    def test_article_delete_url_exists(self):
        response = self.client.get('/readlater/article/delete/1')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<h4>Delete Article</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('article_delete_form', kwargs={'pk': 1}))
        self.assertContains(response, '<h4>Delete Article</h4>', status_code=200)

    def test_article_delete_uses_correct_template(self):
        response = self.client.get('/readlater/article/delete/1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/article_delete_form.html')

    def send_delete_post(self, state):
        self.assertEqual(len(Article.objects.all()), 1)
        url = reverse('article_delete_form', args=(1,))
        response = self.client.post(url + '?' + urlencode({'state': state}),
                                    data={'state': state
                                         }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('article_list_with_state', args=(state,)))
        self.assertEqual(len(Article.objects.all()), 0)

    def test_article_delete_form_state_unread_valid_post(self):
        self.send_delete_post('unread')

    def test_article_delete_form_state_unread_valid_post(self):
        self.send_delete_post('read')


class SettingsViewTest(TestCase):
    NUM_CATEGORIES = 5

    @classmethod
    def setUpTestData(cls):
        for categ_id in range(SettingsViewTest.NUM_CATEGORIES):
            Category.objects.create(name=f'Category {categ_id}')

    def test_settings_url_exists(self):
        response = self.client.get('/readlater/settings/')

        # test that 'Read' is a link to the read page from the unread page
        self.assertContains(response, '<h4>Settings</h4>', status_code=200)

        # also test using name
        response = self.client.get(reverse('settings'))
        self.assertContains(response, '<h4>Settings</h4>', status_code=200)

    def test_settings_uses_correct_template(self):
        response = self.client.get('/readlater/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'readlater/settings_base.html')

    def test_settings_lists_all_categories(self):
        response = self.client.get('/readlater/settings/')
        self.assertEqual(response.status_code, 200)

        # check the number of items in categories list is number created plus one
        # for the uncategorized category created during migration step
        self.assertTrue(len(response.context['category_list']) == SettingsViewTest.NUM_CATEGORIES+1)
