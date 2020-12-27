from datetime import datetime, timezone

from django.test import TestCase
from django.urls import reverse

from readlater.models import Article, Category

MAX_ARTICLE_NAME_LEN = 100
MAX_CATEGORY_NAME_LEN = 100
MAX_NOTES_LEN = 100
MAX_URL_LEN = 400


class CategoryModelTest(TestCase):

    TEST_CATEGORY_NAME = 'TestCategory'

    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name=CategoryModelTest.TEST_CATEGORY_NAME)

    def test_create_uncat_record(self):
        # make sure uncategorized record can be created
        categ = Category.get_uncategorized()
        self.assertEqual(categ.name, 'Uncategorized')

    def test_name_label(self):
        categ = Category.objects.get(name=CategoryModelTest.TEST_CATEGORY_NAME)
        field_label = categ._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_created(self):
        categ = Category.objects.get(name=CategoryModelTest.TEST_CATEGORY_NAME)
        self.assertEqual(categ.name, CategoryModelTest.TEST_CATEGORY_NAME)

    def test_name_maxlen(self):
        categ = Category.objects.get(name=CategoryModelTest.TEST_CATEGORY_NAME)
        max_length = categ._meta.get_field('name').max_length
        self.assertEqual(max_length, MAX_CATEGORY_NAME_LEN)


class ArticleModelTest(TestCase):

    TEST_ARTICLE_NAME = 'TestArticleName'
    TEST_ARTICLE_NOTE = 'TestNotes'
    TEST_ARTICLE_URL = 'http://testurl.org'
    TEST_ARTICLE_PRIORITY = 200
    TEST_ARTICLE_PROGRESS = 100
    TEST_ARTICLE_ADDED = datetime(2020, 12, 1, 10, 20, 30, 0, tzinfo=timezone.utc)
    TEST_ARTICLE_FINISHED = datetime(2020, 12, 2, 10, 20, 30, 0, tzinfo=timezone.utc)
    TEST_ARTICLE_UPDATED = TEST_ARTICLE_FINISHED

    @classmethod
    def setUpTestData(cls):
        categ = Category.objects.get_or_create(name='Category 1')[0]
        Article.objects.create(name=ArticleModelTest.TEST_ARTICLE_NAME,
                               notes=ArticleModelTest.TEST_ARTICLE_NOTE,
                               url=ArticleModelTest.TEST_ARTICLE_URL,
                               category=categ,
                               priority=ArticleModelTest.TEST_ARTICLE_PRIORITY,
                               progress=ArticleModelTest.TEST_ARTICLE_PROGRESS,
                               added_time=ArticleModelTest.TEST_ARTICLE_ADDED,
                               updated_time=ArticleModelTest.TEST_ARTICLE_FINISHED,
                               finished_time=ArticleModelTest.TEST_ARTICLE_UPDATED,
                               )

    @staticmethod
    def _get_test_article():
        return Article.objects.get(name=ArticleModelTest.TEST_ARTICLE_NAME)

    def test_field_label(self):
        fields = dict(name='name',
                      notes='notes',
                      url='url',
                      category='category',
                      priority='priority',
                      progress='progress',
                      added_time='added time',
                      finished_time='finished time',
                      updated_time='updated time',
                      )

        art = self._get_test_article()
        for k, v in fields.items():
            field_label = art._meta.get_field(k).verbose_name
            self.assertEqual(field_label, v)

    def test_name_created(self):
        art = self._get_test_article()
        self.assertEqual(art.name, ArticleModelTest.TEST_ARTICLE_NAME)

    def test_name_maxlen(self):
        art = self._get_test_article()
        max_length = art._meta.get_field('name').max_length
        self.assertEqual(max_length, MAX_ARTICLE_NAME_LEN)

    def test_notes_created(self):
        art = self._get_test_article()
        self.assertEqual(art.notes, ArticleModelTest.TEST_ARTICLE_NOTE)

    def test_notes_maxlen(self):
        art = self._get_test_article()
        max_length = art._meta.get_field('notes').max_length
        self.assertEqual(max_length, MAX_NOTES_LEN)

    def test_url_created(self):
        art = self._get_test_article()
        self.assertEqual(art.url, ArticleModelTest.TEST_ARTICLE_URL)

    def test_url_maxlen(self):
        art = self._get_test_article()
        max_length = art._meta.get_field('url').max_length
        self.assertEqual(max_length, MAX_URL_LEN)

    def test_progress_created(self):
        art = self._get_test_article()
        self.assertEqual(art.progress, ArticleModelTest.TEST_ARTICLE_PROGRESS)

    def test_priority_created(self):
        art = self._get_test_article()
        self.assertEqual(art.priority, ArticleModelTest.TEST_ARTICLE_PRIORITY)

    def test_added_time_created(self):
        art = self._get_test_article()
        self.assertEqual(art.added_time, ArticleModelTest.TEST_ARTICLE_ADDED)

    def test_finished_time_created(self):
        art = self._get_test_article()
        self.assertEqual(art.finished_time, ArticleModelTest.TEST_ARTICLE_FINISHED)

    def test_updated_time_created(self):
        art = self._get_test_article()
        self.assertEqual(art.updated_time, ArticleModelTest.TEST_ARTICLE_UPDATED)

    def test_get_absolute_url(self):
        art = self._get_test_article()
        self.assertEqual(art.get_absolute_url(), reverse('article_list'))

    def test_article_set_uncateg_on_cat_delete(self):
        """ Test that article category is set to 'Uncategorized' if its category is deleted. """
        categ = Category.objects.get_or_create(name='Category 2')[0]
        Article.objects.create(name='Random Article',
                               notes=ArticleModelTest.TEST_ARTICLE_NOTE,
                               url=ArticleModelTest.TEST_ARTICLE_URL,
                               category=categ,
                               priority=ArticleModelTest.TEST_ARTICLE_PRIORITY,
                               progress=ArticleModelTest.TEST_ARTICLE_PROGRESS,
                               added_time=ArticleModelTest.TEST_ARTICLE_ADDED,
                               updated_time=ArticleModelTest.TEST_ARTICLE_FINISHED,
                               finished_time=ArticleModelTest.TEST_ARTICLE_UPDATED,
                               )
        Category.objects.get(name='Category 2').delete()
        art = Article.objects.get(name='Random Article')
        self.assertEqual(art.category.name, 'Uncategorized')
